# Compliance Matrix

| Requirement | File Path | Artifact | Status |
|---|---|---|---|
| Handheld consumer capture protocol | `docs/protocol_stock.md` | Protocol Document | ✅ Complete |
| Tier 3: LiDAR processing | `clean_reconstruct.py` | 3D Point Cloud | ✅ Complete |
| Stitched multi-room plan | `stitch_rooms.py` | Global Pose Graph (`combined_house.ply`) | ✅ Complete |
| Extracted structural dimensions | `process_ply.py` | CAD walls & ceiling height logic | ✅ Complete |
| Damage rule engine | `generate_contract.py` | `configs/rules.json` evaluator | ✅ Complete |
| JSON output matching schema | `generate_contract.py` | `final_contract.json` | ✅ Complete |
| Scope line items & pricing | `generate_contract.py` | `configs/pricing_db.json` matcher | ✅ Complete |
| Fix Loop (25% weight) | `docs/fix_loop_report.md` | Post-mortem Report | ✅ Complete |
| Technical Architecture Report | `docs/technical_report.md` | Narrative Architecture | ⏳ Pending (Drafting next) |
| Benchmark comparison | `docs/benchmark.md` | Head-to-Head Error Table | ⏳ Pending (Requires user input) |
