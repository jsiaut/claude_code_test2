// swift-tools-version:6.0
import PackageDescription
let package = Package(
  name: "chk",
  dependencies: [
    .package(url: "https://github.com/swift-molecules/swift-memory-allocation", branch: "main"),
    .package(url: "https://github.com/jjjkkkjjj/Matft", branch: "main"),
  ],
  targets: [.executableTarget(name: "chk", dependencies: [
    .product(name: "Memory Allocator Arena", package: "swift-memory-allocation"),
    .product(name: "Matft", package: "Matft")])]
)
