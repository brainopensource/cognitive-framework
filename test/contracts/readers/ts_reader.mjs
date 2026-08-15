/**
 * Batch driver for the TypeScript reader.
 *
 * `SC-7` requires two independent implementations to agree on every vector
 * before a schema can be locked. The Python suite in `test/contracts/` owns
 * the vectors and the assertions; this file is only the transport that lets
 * it ask the TypeScript reader the same questions.
 *
 * Reads one JSON request on stdin, writes one JSON response on stdout. No
 * state, no filesystem access beyond the module graph.
 */

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const domain = resolve(here, "../../../vanguard/packages/domain/index.ts");
const {
  canonicalise,
  parseJsonText,
  digestBytes,
  canonicalBytes,
  parse: parsePrimitive,
  unparse,
  PRIMITIVE_KINDS,
  parseSelector,
  decide,
  SELECTOR_KINDS,
} = await import(domain);

const request = JSON.parse(readFileSync(0, "utf8"));
const response = {};

function attempt(fn) {
  try {
    return { ok: true, ...fn() };
  } catch (error) {
    return { ok: false, code: error.code ?? error.name, message: error.message };
  }
}

if (request.canonicalise) {
  response.canonicalise = Object.fromEntries(
    Object.entries(request.canonicalise).map(([name, text]) => [
      name,
      attempt(() => {
        const value = parseJsonText(text);
        const canonical = canonicalise(value);
        return { canonical, digest: digestBytes(canonicalBytes(value)) };
      }),
    ]),
  );
}

if (request.primitives) {
  response.primitives = request.primitives.map(({ kind, value }) =>
    attempt(() => ({ value: unparse(parsePrimitive(kind, value)) })),
  );
  response.primitiveKinds = PRIMITIVE_KINDS;
}

if (request.selectorParse) {
  response.selectorParse = request.selectorParse.map((value) =>
    attempt(() => ({ canonical: canonicalise(parseSelector(value)) })),
  );
  response.selectorKinds = [...SELECTOR_KINDS];
}

if (request.selectorDecide) {
  response.selectorDecide = request.selectorDecide.map(([parent, child]) => decide(parent, child));
}

process.stdout.write(JSON.stringify(response));
