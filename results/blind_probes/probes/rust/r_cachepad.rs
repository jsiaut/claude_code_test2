#![feature(mpmc_channel)]
use std::sync::mpmc::utils::CachePadded;
fn main(){ let _c = CachePadded::new(0u64); }
