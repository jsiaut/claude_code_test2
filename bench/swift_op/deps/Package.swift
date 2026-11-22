// swift-tools-version:6.1
// v4, point 6 (docs/V4_OPEN.md, 5.2) : bibliothèques de la copie bench/swift_op, construites par SwiftPM hors du dépôt
// (build.sh : swift build -c release, donc -O et module entier, plus -target-cpu native pour toutes les cibles) ; ms
// est ensuite compilé par la commande publiée, ces modules en plus. Version figée : results/open/versions.txt.
import PackageDescription
let package = Package(
  name: "swift_op_deps",
  products: [.library(name: "OpDeps", type: .static, targets: ["OpDeps"])],
  dependencies: [
    .package(url: "https://github.com/swift-molecules/swift-memory-allocation",
             revision: "8742a8c9117c78f905d42c765198b44f0eade34b", traits: ["MemoryAllocatorArena"]),
  ],
  targets: [.target(name: "OpDeps", dependencies: [
    .product(name: "Memory Allocator Arena", package: "swift-memory-allocation")])]
)
