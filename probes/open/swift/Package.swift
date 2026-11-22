// swift-tools-version:6.1
// v4, point 6 (docs/V4_OPEN.md, 4) : sondes de la grille ouverte de Swift (B2 : swift-memory-allocation, arène ;
// F1 : Matft 1.0.1). Construction hors du dépôt : swift build --scratch-path /opt/open/swift/build.
import PackageDescription
let package = Package(
  name: "open_probe",
  dependencies: [
    .package(url: "https://github.com/swift-molecules/swift-memory-allocation",
             revision: "8742a8c9117c78f905d42c765198b44f0eade34b", traits: ["MemoryAllocatorArena"]),
    .package(url: "https://github.com/jjjkkkjjj/Matft", exact: "1.0.1"),
  ],
  targets: [.executableTarget(name: "probe", dependencies: [
    .product(name: "Memory Allocator Arena", package: "swift-memory-allocation"),
    .product(name: "Matft", package: "Matft")],
    swiftSettings: [.unsafeFlags(["-Ounchecked", "-target-cpu", "native"])])]
)
