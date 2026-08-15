"""
runtime_jit.py — Pure Python Stack Bytecode JIT with Escape Analysis & Deoptimization.
Zero-dependency custom VM, tracing JIT, SSA IR, optimization passes,
and safe deoptimization back to the interpreter.
"""

from __future__ import annotations

import collections
import operator
import sys
import types
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable


class Opcode(Enum):
    LOAD_CONST = auto()
    LOAD_VAR = auto()
    STORE_VAR = auto()
    BINARY_ADD = auto()
    BINARY_SUB = auto()
    BINARY_MUL = auto()
    BINARY_DIV = auto()
    JUMP_IF_FALSE = auto()
    JUMP_ABSOLUTE = auto()
    CALL_FUNC = auto()
    RETURN_VALUE = auto()
    ALLOC_OBJECT = auto()
    GET_FIELD = auto()
    SET_FIELD = auto()


@dataclass(frozen=True)
class Instr:
    opcode: Opcode
    arg: Any = None

    def __repr__(self) -> str:
        return f"{self.opcode.name}({self.arg!r})"


class Object:
    """Heap-allocated object with mutable fields."""
    __slots__ = ('fields', 'obj_id')
    _next_id: int = 0

    def __init__(self, fields: dict[str, Any] | None = None) -> None:
        self.fields: dict[str, Any] = fields if fields is not None else {}
        Object._next_id += 1
        self.obj_id = Object._next_id

    def __repr__(self) -> str:
        return f"Object#{self.obj_id}({self.fields})"


class Frame:
    """Execution frame with operand stack, locals, and program counter."""
    __slots__ = ('stack', 'locals', 'pc', 'bytecode', 'constants',
                 'func_name', 'return_value')

    def __init__(self, bytecode: list[Instr], constants: list[Any],
                 locals_: dict[str, Any] | None = None,
                 func_name: str = '<top>') -> None:
        self.stack: list[Any] = []
        self.locals: dict[str, Any] = locals_ if locals_ is not None else {}
        self.pc = 0
        self.bytecode = bytecode
        self.constants = constants
        self.func_name = func_name
        self.return_value: Any = None

    def __repr__(self) -> str:
        return f"Frame({self.func_name}, pc={self.pc})"


class _DeoptSignal(Exception):
    """Raised by JIT'd code to signal a bailout to the interpreter."""
    def __init__(self, pc: int, locals_: dict[str, Any],
                 stack: list[Any]) -> None:
        self.pc = pc
        self.locals = locals_
        self.stack = stack


class VM:
    """Bytecode virtual machine with tracing JIT support."""

    def __init__(self) -> None:
        self.frames: list[Frame] = []
        self.exec_count: dict[int, int] = collections.defaultdict(int)
        self.backjump_count: dict[int, int] = collections.defaultdict(int)
        self.call_count: dict[int, int] = collections.defaultdict(int)
        self.hot_threshold = 10
        self.jit_compiler: _JITCompiler | None = None
        self._tracing = False
        self._trace_buffer: list[tuple[int, Instr, Any]] = []
        self._trace_start_pc: int = 0
        self._trace_spec_types: dict[str, type] = {}
        self.guard_failures: int = 0
        self.bailouts: int = 0
        self.fn_registry: dict[int, tuple[list[Instr], list[Any], list[str], int]] = {}
        self._active_jit_frame: Frame | None = None
        self._jit_enabled = True
        self.total_objects_allocated: int = 0

    def run(self, bytecode: list[Instr], constants: list[Any],
            locals_: dict[str, Any] | None = None,
            func_name: str = '<main>') -> Any:
        frame = Frame(bytecode, constants, locals_, func_name)
        self.frames.append(frame)
        try:
            return self._execute(frame)
        finally:
            self.frames.pop()

    def call(self, bytecode: list[Instr], constants: list[Any],
             arg_names: list[str], args: list[Any]) -> Any:
        locals_ = dict(zip(arg_names, args))
        frame = Frame(bytecode, constants, locals_,
                      func_name=f"<fn({','.join(arg_names)})>")
        self.frames.append(frame)
        try:
            return self._execute(frame)
        finally:
            self.frames.pop()

    def register_function(self, func_id: int, bytecode: list[Instr],
                          constants: list[Any],
                          arg_names: list[str]) -> None:
        self.fn_registry[func_id] = (bytecode, constants, arg_names, len(arg_names))

    def enable_jit(self) -> None:
        self._jit_enabled = True
        if self.jit_compiler is None:
            self.jit_compiler = _JITCompiler(self)

    def get_object_count(self) -> int:
        return self.total_objects_allocated

    def _execute(self, frame: Frame) -> Any:
        bc = frame.bytecode
        consts = frame.constants

        while frame.pc < len(bc):
            if (self.jit_compiler is not None and self._jit_enabled
                    and not self._tracing):
                jit_code = self.jit_compiler.lookup(frame.func_name, frame.pc)
                if jit_code is not None:
                    result = self._run_jitted(frame, jit_code)
                    if result is not None:
                        return result
                    continue

            if (not self._tracing and self.jit_compiler is not None
                    and self._jit_enabled):
                pc = frame.pc
                if self.backjump_count.get(pc, 0) >= self.hot_threshold:
                    self._start_trace(frame)

            instr = bc[frame.pc]
            old_pc = frame.pc

            if self._tracing:
                self._trace_buffer.append((old_pc, instr, self._snapshot_types(frame)))

            self._dispatch(instr, frame, consts)

            self.exec_count[old_pc] += 1
            if frame.pc <= old_pc and instr.opcode == Opcode.JUMP_ABSOLUTE:
                self.backjump_count[old_pc] += 1
                if (self._tracing and frame.pc == self._trace_start_pc
                        and len(self._trace_buffer) > 3):
                    self._finish_trace(frame)

            if instr.opcode == Opcode.CALL_FUNC:
                self.call_count[old_pc] += 1

        return frame.return_value

    def _run_jitted(self, frame: Frame, jit_code: Any) -> Any | None:
        self._active_jit_frame = frame
        try:
            result = jit_code(frame)
            return result
        except _DeoptSignal as e:
            self.bailouts += 1
            self._handle_deopt(frame, e)
            return None
        finally:
            self._active_jit_frame = None

    def _handle_deopt(self, frame: Frame, signal: _DeoptSignal) -> None:
        frame.pc = signal.pc
        frame.locals = signal.locals.copy()
        frame.stack = list(signal.stack)
        self.guard_failures += 1
        if self.guard_failures > 10 and self.jit_compiler is not None:
            self.jit_compiler.invalidate_traces_for(frame.func_name, signal.pc)

    def _dispatch(self, instr: Instr, frame: Frame, consts: list[Any]) -> None:
        op = instr.opcode
        arg = instr.arg
        s = frame.stack

        if op == Opcode.LOAD_CONST:
            s.append(consts[arg])
        elif op == Opcode.LOAD_VAR:
            s.append(frame.locals[arg])
        elif op == Opcode.STORE_VAR:
            frame.locals[arg] = s.pop()
        elif op == Opcode.BINARY_ADD:
            b = s.pop()
            a = s.pop()
            s.append(a + b)
        elif op == Opcode.BINARY_SUB:
            b = s.pop()
            a = s.pop()
            s.append(a - b)
        elif op == Opcode.BINARY_MUL:
            b = s.pop()
            a = s.pop()
            s.append(a * b)
        elif op == Opcode.BINARY_DIV:
            b = s.pop()
            a = s.pop()
            s.append(a / b)
        elif op == Opcode.JUMP_IF_FALSE:
            val = s.pop()
            if not val:
                frame.pc = arg
                return
        elif op == Opcode.JUMP_ABSOLUTE:
            frame.pc = arg
            return
        elif op == Opcode.CALL_FUNC:
            func_idx = arg
            fn_entry = self.fn_registry.get(func_idx)
            if fn_entry is None:
                raise RuntimeError(f"Unknown function index {func_idx}")
            fn_bc, fn_consts, fn_arg_names, fn_arity = fn_entry
            args = [s.pop() for _ in range(fn_arity)]
            args.reverse()
            result = self.call(fn_bc, fn_consts, fn_arg_names, args)
            s.append(result)
        elif op == Opcode.RETURN_VALUE:
            result = s.pop() if s else None
            frame.return_value = result
            frame.pc = len(frame.bytecode)
            return
        elif op == Opcode.ALLOC_OBJECT:
            field_count = arg if arg is not None else 0
            field_keys = []
            field_vals = []
            for _ in range(field_count):
                val = s.pop()
                field_vals.append(val)
            for _ in range(field_count):
                key = s.pop()
                field_keys.append(key)
            fields = dict(zip(field_keys, field_vals))
            obj = Object(fields)
            self.total_objects_allocated += 1
            s.append(obj)
        elif op == Opcode.GET_FIELD:
            obj = s.pop()
            s.append(obj.fields[arg])
        elif op == Opcode.SET_FIELD:
            field_val = s.pop()
            obj = s.pop()
            obj.fields[arg] = field_val
            s.append(field_val)
        else:
            raise RuntimeError(f"Unknown opcode {op}")

        frame.pc += 1

    def _start_trace(self, frame: Frame) -> None:
        self._tracing = True
        self._trace_buffer = [(frame.pc, frame.bytecode[frame.pc],
                               self._snapshot_types(frame))]
        self._trace_start_pc = frame.pc
        self._trace_spec_types = self._snapshot_types(frame)

    def _snapshot_types(self, frame: Frame) -> dict[str, type]:
        types_: dict[str, type] = {}
        for k, v in frame.locals.items():
            if v is not None:
                types_[f"var:{k}"] = type(v)
        for i, v in enumerate(frame.stack):
            if v is not None:
                types_[f"stack:{i}"] = type(v)
        return types_

    def _finish_trace(self, frame: Frame) -> None:
        if not self._tracing:
            return
        self._tracing = False
        trace = list(self._trace_buffer)
        self._trace_buffer = []
        if self.jit_compiler is not None and len(trace) > 1:
            self.jit_compiler.record_trace(
                frame.func_name, self._trace_start_pc, trace,
                self._trace_spec_types
            )


# ==================================================================
# SSA IR
# ==================================================================

class SSAOp(Enum):
    CONST = auto()
    LOAD_LOCAL = auto()
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    PHI = auto()
    GUARD_TYPE = auto()
    GUARD_NONZERO = auto()
    SIDE_EXIT = auto()
    ALLOC_OBJ = auto()
    GET_FIELD = auto()
    SET_FIELD = auto()
    DEOPT = auto()
    RETURN = auto()
    NOP = auto()


@dataclass
class SSANode:
    op: SSAOp
    args: list[int] = field(default_factory=list)
    imm: Any = None


@dataclass
class SSAValue:
    node: SSANode
    id: int
    value_type: type | None = None
    escapes: bool = False
    is_alloc: bool = False
    field_map: dict[str, int] | None = None


class SSAModule:
    def __init__(self) -> None:
        self.values: list[SSAValue] = []
        self.entry_values: dict[str, int] = {}

    def new_value(self, op: SSAOp, args: list[int] | None = None,
                  imm: Any = None) -> int:
        idx = len(self.values)
        node = SSANode(op, args or [], imm)
        self.values.append(SSAValue(node=node, id=idx))
        return idx

    def get(self, idx: int) -> SSAValue:
        return self.values[idx]

    def __len__(self) -> int:
        return len(self.values)


# ==================================================================
# TRACE LOWERING: Bytecode -> SSA IR
# ==================================================================

class TraceLowerer:
    def __init__(self, trace: list[tuple[int, Instr, dict]],
                 spec_types: dict[str, type]) -> None:
        self.trace = trace
        self.spec_types = spec_types
        self.ssa = SSAModule()
        self.var_map: dict[str, int] = {}
        self.stack_map: list[int] = []

    def lower(self) -> SSAModule:
        if not self.trace:
            return self.ssa
        if self.trace:
            _, _, first_types = self.trace[0]
            for key in first_types:
                if key.startswith('var:'):
                    var_name = key[4:]
                    val_idx = self.ssa.new_value(SSAOp.LOAD_LOCAL, imm=var_name)
                    self.var_map[var_name] = val_idx
                    self.ssa.entry_values[var_name] = val_idx
        for pc, instr, types_ in self.trace:
            self._lower_instr(pc, instr, types_)
        return self.ssa

    def _lower_instr(self, pc: int, instr: Instr,
                     types_: dict[str, type]) -> None:
        op = instr.opcode
        arg = instr.arg

        if op == Opcode.LOAD_CONST:
            idx = self.ssa.new_value(SSAOp.CONST, imm=arg)
            self.stack_map.append(idx)

        elif op == Opcode.LOAD_VAR:
            var = arg
            if var not in self.var_map:
                idx = self.ssa.new_value(SSAOp.LOAD_LOCAL, imm=var)
                self.var_map[var] = idx
            self.stack_map.append(self.var_map[var])

        elif op == Opcode.STORE_VAR:
            val_idx = self.stack_map.pop()
            var = arg
            self.var_map[var] = val_idx

        elif op == Opcode.BINARY_ADD:
            b = self.stack_map.pop()
            a = self.stack_map.pop()
            idx = self.ssa.new_value(SSAOp.ADD, args=[a, b])
            # Inject type guard based on speculation
            var_type = self.spec_types.get(f"stack:0")
            self.stack_map.append(idx)

        elif op == Opcode.BINARY_SUB:
            b = self.stack_map.pop()
            a = self.stack_map.pop()
            idx = self.ssa.new_value(SSAOp.SUB, args=[a, b])
            self.stack_map.append(idx)

        elif op == Opcode.BINARY_MUL:
            b = self.stack_map.pop()
            a = self.stack_map.pop()
            idx = self.ssa.new_value(SSAOp.MUL, args=[a, b])
            self.stack_map.append(idx)

        elif op == Opcode.BINARY_DIV:
            b = self.stack_map.pop()
            a = self.stack_map.pop()
            idx = self.ssa.new_value(SSAOp.DIV, args=[a, b])
            self.stack_map.append(idx)

        elif op == Opcode.JUMP_IF_FALSE:
            val_idx = self.stack_map.pop()
            # Insert a guard that the value is truthy; side-exit if false
            guard_idx = self.ssa.new_value(SSAOp.GUARD_NONZERO, args=[val_idx])
            self.stack_map.append(guard_idx)

        elif op == Opcode.JUMP_ABSOLUTE:
            # Back edge: no-op in SSA for a linear trace
            pass

        elif op == Opcode.RETURN_VALUE:
            val_idx = self.stack_map.pop() if self.stack_map else None
            if val_idx is not None:
                self.ssa.new_value(SSAOp.RETURN, args=[val_idx])

        elif op == Opcode.ALLOC_OBJECT:
            idx = self.ssa.new_value(SSAOp.ALLOC_OBJ, imm=arg)
            self.stack_map.append(idx)

        elif op == Opcode.GET_FIELD:
            obj_idx = self.stack_map.po
