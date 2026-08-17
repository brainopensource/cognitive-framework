import { useEffect, useRef, useState } from "react";
import Editor, { type OnMount } from "@monaco-editor/react";
import type { WorkspaceFile } from "./files";
import { SlotFrame } from "./files";

export function EditorSlot({ file }: { file?: WorkspaceFile }) {
  const [value, setValue] = useState(file?.content ?? "Select a file from the workspace tree.");
  const editorRef = useRef<Parameters<OnMount>[0] | null>(null);
  const monacoRef = useRef<Parameters<OnMount>[1] | null>(null);
  useEffect(() => { setValue(file?.content ?? "Select a file from the workspace tree."); }, [file]);
  const onMount: OnMount = (editor, monaco) => { editorRef.current = editor; monacoRef.current = monaco; };
  useEffect(() => { const editor = editorRef.current; const monaco = monacoRef.current; if (!editor || !monaco || !file) return; const previous = editor.getModel(); if (previous) previous.dispose(); editor.setModel(monaco.editor.createModel(file.content, file.language, monaco.Uri.parse(`inmemory://vanguard/${file.path}`))); return () => { const model = editor.getModel(); if (model) model.dispose(); }; }, [file]);
  useEffect(() => () => { const model = editorRef.current?.getModel(); if (model) model.dispose(); }, []);
  return <SlotFrame title="MONACO EDITOR"><div className="editor-meta"><span>{file?.path ?? "no file selected"}</span><span>UTF-8 · Monarch tokenization · LSP: Phase 4</span></div><Editor height="430px" theme="vs-dark" language={file?.language ?? "plaintext"} value={value} onChange={next => setValue(next ?? "")} onMount={onMount} options={{ minimap: { enabled: false }, fontSize: 13, automaticLayout: true }} /></SlotFrame>;
}
