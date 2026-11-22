// Contre-épreuve de la sonde D3 : le type de bourrage de cordyceps n'est pas public (pub(crate) dans src/util.rs).
use cordyceps::util::CachePadded;
fn main() {
    let x = CachePadded(0u64);
    println!("{}", std::mem::size_of_val(&x));
}
