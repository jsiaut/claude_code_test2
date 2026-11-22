// swift-tools-version:6.0
import PackageDescription
let package = Package(
  name: "chk",
  dependencies: [.package(url: "https://github.com/jjjkkkjjj/Matft", exact: "1.0.1")],
  targets: [.executableTarget(name: "chk", dependencies: [.product(name: "Matft", package: "Matft")])]
)
