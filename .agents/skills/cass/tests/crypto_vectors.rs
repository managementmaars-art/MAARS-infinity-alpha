use coding_agent_search::encryption::{
    Argon2Params, aes_gcm_decrypt, aes_gcm_encrypt, argon2id_hash, hkdf_extract_expand,
};
use serde::Deserialize;

#[derive(Deserialize)]
struct AesGcmVector {
    name: String,
    key: String,
    nonce: String,
    plaintext: String,
    aad: String,
    ciphertext: String,
    tag: String,
}

#[derive(Deserialize)]
#[allow(dead_code)]
struct Argon2Vector {
    name: String,
    password: String,
    salt: String,
    memory_kb: u32,
    iterations: u32,
    parallelism: u32,
    output_len: u32,
    expected_hash_hex: String,
}

#[derive(Deserialize)]
struct HkdfVector {
    name: String,
    ikm: String,
    salt: String,
    info: String,
    output_len: usize,
    expected_okm: String,
}

fn load_test_vectors<T: for<'de> Deserialize<'de>>(filename: &str) -> Vec<T> {
    let path = std::path::PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("tests/vectors")
        .join(filename);
    let f = std::fs::File::open(path).expect("failed to open vector file");
    serde_yaml::from_reader(f).expect("failed to parse yaml")
}

#[test]
fn test_aes_gcm_vectors() {
    let vectors: Vec<AesGcmVector> = load_test_vectors("aes_gcm.yaml");
    for v in vectors {
        let key = hex::decode(&v.key).unwrap();
        let nonce = hex::decode(&v.nonce).unwrap();
        let plaintext = hex::decode(&v.plaintext).unwrap();
        let aad = hex::decode(&v.aad).unwrap();
        let expected_ciphertext = hex::decode(&v.ciphertext).unwrap();
        let expected_tag = hex::decode(&v.tag).unwrap();

        let (ciphertext, tag) = aes_gcm_encrypt(&key, &nonce, &plaintext, &aad).unwrap();

        assert_eq!(
            ciphertext, expected_ciphertext,
            "Ciphertext mismatch for {}",
            v.name
        );
        assert_eq!(tag, expected_tag, "Tag mismatch for {}", v.name);

        let decrypted =
            aes_gcm_decrypt(&key, &nonce, &ciphertext, &aad, &tag).expect("decryption failed");
        assert_eq!(decrypted, plaintext, "Decryption mismatch for {}", v.name);
    }
}

#[test]
fn test_argon2_vectors() {
    let vectors: Vec<Argon2Vector> = load_test_vectors("argon2.yaml");
    for v in vectors {
        let password = v.password.as_bytes();
        let salt = v.salt.as_bytes();
        let params = Argon2Params::new(
            v.memory_kb,
            v.iterations,
            v.parallelism,
            Some(v.output_len as usize),
        )
        .unwrap();

        let expected = hex::decode(&v.expected_hash_hex).unwrap();
        let result = argon2id_hash(password, salt, &params).unwrap();

        assert_eq!(result, expected, "Argon2 mismatch for {}", v.name);
    }
}

#[test]
fn test_hkdf_vectors() {
    let vectors: Vec<HkdfVector> = load_test_vectors("hkdf.yaml");
    for v in vectors {
        let ikm = hex::decode(v.ikm).unwrap();
        let salt = hex::decode(v.salt).unwrap();
        let info = hex::decode(v.info).unwrap();
        let expected_okm = hex::decode(&v.expected_okm).unwrap();

        // This function performs both extract and expand
        let result = hkdf_extract_expand(&ikm, &salt, &info, v.output_len).unwrap();

        assert_eq!(result, expected_okm, "HKDF vector failed: {}", v.name);
    }
}
