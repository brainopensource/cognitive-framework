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
from typing import Any, Callable, NoReturn

# ──────────────────────────────────────────────────────────────────────
# 1.  OPCODES & BYTECODE DEFINITION
# ──────────────────────────────────────────────────────────────────────

class Opcode(Enum):
    LOAD_CONST     = auto()
    LOAD_VAR       = auto()
    STORE_VAR      = auto()
    BINARY_ADD     = auto()
    BINARY_SUB     = auto()
    BINARY_MUL     = auto()
    BINARY_DIV     = auto()
    JUMP_IF_FALSE  = auto()
    JUMP_ABSOLUTE  = auto()
    CALL_FUNC      = auto()
    RETURN_VALUE   = auto()
    ALLOC_OBJECT   = auto()
    GET_FIELD      = auto()
    SET_FIELD      = auto()


@dataclass(frozen=True)
class Instr:
    """A single bytecode instruction with optional argument."""
    opcode: Opcode
    arg: Any = None

    def __repr__(self) -> str:
        return f"{self.opcode.name}({self.arg!r})"


# ──────────────────────────────────────────────────────────────────────
# 2.  INTERPRETER STATE & VALUE REPRESENTATION
# ──────────────────────────────────────────────────────────────────────

class Object:
    """Heap-allocated object with mutable fields (dynamically typed)."""
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

    def peek_stack(self, depth: int = 0) -> Any:
        return self.stack[-1 - depth]

    def __repr__(self) -> str:
        return f"Frame({self.func_name}, pc={self.pc})"


# ──────────────────────────────────────────────────────────────────────
# 3.  BASELINE INTERPRETER
# ──────────────────────────────────────────────────────────────────────

class VM:
    """Bytecode virtual machine with execution counters for hot-loop detection."""

    def __init__(self) -> None:
        self.frames: list[Frame] = []
        self.exec_count: dict[int, int] = collections.defaultdict(int)
        self.backjump_count: dict[int, int] = collections.defaultdict(int)
        self.call_count: dict[int, int] = collections.defaultdict(int)
        self.hot_threshold = 10

        # JIT integration
        self.jit_compiler: _JITCompiler | None = None

        # Tracing state
        self._tracing = False
        self._trace_buffer: list[tuple[int, Instr, Any]] = []
        self._trace_start_pc: int = 0
        self._trace_spec_types: dict[str, type] = {}

        # Deopt statistics
        self.guard_failures: int = 0
        self.bailouts: int = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, bytecode: list[Instr], constants: list[Any],
            locals_: dict[str, Any] | None = None,
            func_name: str = '<main>') -> Any:
        """Execute bytecode in a new frame."""
        frame = Frame(bytecode, constants, locals_, func_name)
        self.frames.append(frame)
        try:
            return self._execute(frame)
        finally:
            self.frames.pop()

    def call(self, bytecode: list[Instr], constants: list[Any],
             arg_names: list[str], args: list[Any]) -> Any:
        """Call a function by creating a new frame."""
        locals_ = dict(zip(arg_names, args))
        frame = Frame(bytecode, constants, locals_,
                      func_name=f"<fn({','.join(arg_names)})>")
        self.frames.append(frame)
        try:
            return self._execute(frame)
        finally:
            self.frames.pop()

    # ------------------------------------------------------------------
    # Core execution loop
    # ------------------------------------------------------------------

    def _execute(self, frame: Frame) -> Any:
        bc = frame.bytecode
        consts = frame.constants

        while frame.pc < len(bc):
            # ---- JIT dispatch --------------------------------------------------
            if self.jit_compiler is not None and not self._tracing:
                jit_code = self.jit_compiler.lookup(frame.func_name, frame.pc)
                if jit_code is not None:
                    result = jit_code(frame)
                    if result is not None:
                        return result
                    continue

            # ---- Tracing setup ------------------------------------------------
            if not self._tracing and self.jit_compiler is not None:
                if self.backjump_count[frame.pc] >= self.hot_threshold:
                    self._start_trace(frame)

            # ---- Fetch & execute ----------------------------------------------
            instr = bc[frame.pc]
            old_pc = frame.pc

            if self._tracing:
                self._trace_buffer.append((old_pc, instr, self._snapshot_types(frame)))

            self._dispatch(instr, frame, consts)

            # ---- Counter bookkeeping -------------------------------------------
            self.exec_count[old_pc] += 1
            if frame.pc <= old_pc and instr.opcode == Opcode.JUMP_ABSOLUTE:
                self.backjump_count[old_pc] += 1
                if (self._tracing and frame.pc == self._trace_start_pc
                        and len(self._trace_buffer) > 3):
                    self._finish_trace(frame)

            if instr.opcode == Opcode.CALL_FUNC:
                self.call_count[old_pc] += 1

        return frame.return_value

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
            # Look up the function from a registry
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
            frame.pc = len(frame.bytecode)  # terminate
            return
        elif op == Opcode.ALLOC_OBJECT:
            field_count = arg if arg is not None else 0
            fields = {}
            for _ in range(field_count):
                val = s.pop()
                # Field names are stored as consts on the stack as a list preceding alloc
                pass
            obj = Object(fields)
            s.append(obj)
        elif op == Opcode.GET_FIELD:
            obj = s.pop()
            s.append(obj.fields[arg])
        elif op == Opcode.SET_FIELD:
            obj = s.pop()
            val = s.pop()
            obj.fields[arg] = val
            s.append(val)  # push back for expression usage
        else:
            raise RuntimeError(f"Unknown opcode {op}")

        frame.pc += 1

    # ------------------------------------------------------------------
    # Function registry
    # ------------------------------------------------------------------

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

    def register_function(self, func_id: int, bytecode: list[Instr],
                          constants: list[Any],
                          arg_names: list[str]) -> None:
        self.fn_registry[func_id] = (bytecode, constants, arg_names, len(arg_names))

    # ------------------------------------------------------------------
    # Tracing
    # ------------------------------------------------------------------

    def _start_trace(self, frame: Frame) -> None:
        self._tracing = True
        self._trace_buffer = []
        self._trace_start_pc = frame.pc
        self._trace_spec_types = {}

    def _snapshot_types(self, frame: Frame) -> dict[str, type]:
        types_ = {}
        for k, v in frame.locals.items():
            if v is not None:
                types_[k] = type(v)
        for i, v in enumerate(frame.stack):
            if v is not None:
                types_[f"$stack_{i}"] = type(v)
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


# ──────────────────────────────────────────────────────────────────────
# 4.  SSA IR DEFINITION
# ──────────────────────────────────────────────────────────────────────

class SSAOp(Enum):
    CONST      = auto()
    LOAD_ARG   = auto()
    ADD        = auto()
    SUB        = auto()
    MUL        = auto()
    DIV        = auto()
    PHI        = auto()
    STORE_LOCAL = auto()
    LOAD_LOCAL  = auto()
    GUARD_TYPE  = auto()
    GUARD_TRUE  = auto()
    SIDE_EXIT   = auto()

    # Object operations
    ALLOC_OBJ   = auto()
    GET_FIELD   = auto()
    SET_FIELD   = auto()
    DEOPT       = auto()
    GUARD_ESCAPE = auto()


@dataclass
class SSANode:
    op: SSAOp
    args: list[int] = field(default_factory=list)   # SSA value indices
    imm: Any = None                                 # immediate value
    block: int = 0                                  # basic block id


@dataclass
class SSABlock:
    id: int
    params: list[int] = field(default_factory=list)  # block param SSA indices
    nodes: list[int] = field(default_factory=list)   # SSA value indices in block
    terminator: str | None = None                    # 'fallthrough', 'branch', 'side_exit'


class SSAModule:
    """SSA IR module: flat list of values + basic blocks."""
    def __init__(self) -> None:
        self.values: list[SSANode] = []
        self.blocks: list[SSABlock] = []
        self.entry_block: int = 0

    def new_value(self, op: SSAOp, args: list[int] | None = None,
                  imm: Any = None, block: int = 0) -> int:
        idx = len(self.values)
        self.values.append(SSANode(op, args or [], imm, block))
        return idx

    def new_block(self) -> int:
        bid = len(self.blocks)
        self.blocks.append(SSABlock(id=bid))
        return bid


# ──────────────────────────────────────────────────────────────────────
# 5.  TRACE LOWERING: Bytecode → SSA IR
# ──────────────────────────────────────────────────────────────────────

class TraceLowerer:
    """Lower a linear execution trace into SSA IR with Phi nodes at loop headers."""

    def __init__(self, trace: list[tuple[int, Instr, dict]],
                 spec_types: dict[str, type]) -> None:
        self.trace = trace
        self.spec_types = spec_types

        # Mapping from interpreter local name → SSA value index
        self.var_map: dict[str, int] = {}
        self.stack_map: list[int] = []  # SSA indices for interpreter stack

        self.ssa = SSAModule()
        self.block_id = 0
        self.loop_header_pc: int | None = None

        # Track loop header info for phi placement
        self.loop_header_ssa_idx: int | None = None
        self.back_edge_values: dict[str, int] = {}  # var → SSA idx entering loop body

    def lower(self) -> SSAModule:
        """Lower the trace into SSA IR."""
        if not self.trace:
            return self.ssa

        # Determine loop header from first backjump
        self._find_loop_header()

        entry = self.ssa.new_block()
        self.ssa.entry_block = entry

        # Create phi values for all local vars at loop header
        if self.loop_header_pc is not None:
            _, first_instr, _ = self.trace[0]
            assert first_instr.opcode == Opcode.JUMP_ABSOLUTE
            # The trace starts at the target of the backjump; find what vars are live
            self._create_phis()

        # Lower each instruction
        for pc, instr, types_ in self.trace:
            self._lower_instr(pc, instr, types_)

        return self.ssa

    def _find_loop_header(self) -> None:
        for pc, instr, _ in self.trace:
            if instr.opcode == Opcode.JUMP_ABSOLUTE and pc == len(self.trace) - 1:
                # Last instruction is the backjump; target is the loop header
                self.loop_header_pc = instr.arg
                break

    def _get_live_vars(self) -> set[str]:
        """Approximate live vars from the first frame snapshot."""
        if not self.trace:
            return set()
        _, _, types_ = self.trace[0]
        # Types dict contains $stack_N entries and var names; vars are non-$ entries
        return {k for k in types_ if not k.startswith('$stack_')}

    def _create_phis(self) -> None:
        live = self._get_live_vars()
        for var in live:
            # Create a place-holder phi (pre-header value later filled)
            phi_idx = self.ssa.new_value(SSAOp.PHI, block=self.block_id)
            self.var_map[var] = phi_idx

    def _lower_instr(self, pc: int, instr: Instr,
                     types_: dict[str, type]) -> None:
        op = instr.opcode
        arg = instr.arg

        if op == Opcode.LOAD_CONST:
            const_idx = arg
            # Try to re-use existing const SSA values
            val = self.ssa.new_value(SSAOp.CONST, imm=const_idx,
                                     block=self.block_id)
            self.stack_map.append(val)

        elif op == Opcode.LOAD_VAR:
            var = arg
            if var in self.var_map:
                ssa_idx = self.v