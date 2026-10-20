# Actual Mali-G57 cbuf driver fixture

Self-authored source/data, run through principal with a 45-second child bound.
result.json records the FAILED default EGLDisplay initialization. result-gbm.json
records the successful explicit GBM + surfaceless FBO attempt; samples.json parses
that exact raw stdout. Ten draw/readback checks match finite expected values.
Both cleanup receipts have zero errors. No window/swap/modeset/audio/game assets.

Limited proof: lane/row addressing, one scalar half-conversion value, texel update
and texture/unit rebinding. Not NaN payloads, full f16 semantics, production
context/in-flight resource lifetime or correct game pixels/FPS.
