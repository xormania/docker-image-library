pub fn answer() -> u32 {
    42
}

#[cfg(test)]
mod tests {
    #[test]
    fn native_behavior() {
        assert_eq!(super::answer(), 42);
    }
}
