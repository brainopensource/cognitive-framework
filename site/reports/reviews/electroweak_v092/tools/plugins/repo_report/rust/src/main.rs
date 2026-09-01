use std::{env, fs, path::{Path, PathBuf}};

const SKIP: [&str; 9] = [".git", ".venv", "node_modules", "__pycache__", ".lda", ".generated", "site", "dist", "build"];

fn skipped(path: &Path) -> bool {
    path.components().any(|c| SKIP.iter().any(|x| c.as_os_str() == *x))
}

fn walk(root: &Path, path: &Path) {
    let Ok(entries) = fs::read_dir(path) else { return };
    for entry in entries.flatten() {
        let p = entry.path();
        if skipped(&p) { continue; }
        if p.is_dir() { walk(root, &p); continue; }
        let Ok(meta) = fs::metadata(&p) else { continue; };
        let rel = p.strip_prefix(root).unwrap_or(&p).to_string_lossy().replace('\\', "/");
        let bytes = fs::read(&p).map(|x| x.len()).unwrap_or(meta.len() as usize);
        let lines = fs::read(&p).map(|x| x.iter().filter(|b| **b == b'\n').count() + 1).unwrap_or(0);
        println!("{}\t{}\t{}", rel, bytes, lines);
    }
}

fn main() {
    let root = env::args().nth(1).map(PathBuf::from).unwrap_or_else(|| PathBuf::from("."));
    walk(&root, &root);
}
