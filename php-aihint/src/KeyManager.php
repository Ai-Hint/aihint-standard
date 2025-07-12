<?php
namespace AIHint;

use Exception;

class KeyManager {
    private $keySize = 2048;
    private $digestAlgo = 'sha256';

    public function generateKeys(string $outputDir): void {
        if (!is_dir($outputDir)) {
            if (!mkdir($outputDir, 0755, true)) {
                throw new Exception("Failed to create output directory: $outputDir");
            }
        }

        // Generate private key with modern configuration
        $config = [
            'private_key_bits' => $this->keySize,
            'private_key_type' => OPENSSL_KEYTYPE_RSA,
            'digest_alg' => 'sha256',
        ];

        $privateKey = openssl_pkey_new($config);

        if (!$privateKey) {
            $error = openssl_error_string();
            throw new Exception("Failed to generate private key: " . ($error ?: "Unknown error"));
        }

        // Extract private key
        $privateKeyExport = openssl_pkey_export($privateKey, $privateKeyPem);
        if (!$privateKeyExport) {
            $error = openssl_error_string();
            throw new Exception("Failed to export private key: " . ($error ?: "Unknown error"));
        }

        // Extract public key
        $publicKeyDetails = openssl_pkey_get_details($privateKey);
        if (!$publicKeyDetails) {
            $error = openssl_error_string();
            throw new Exception("Failed to get public key details: " . ($error ?: "Unknown error"));
        }
        
        $publicKeyPem = $publicKeyDetails['key'];

        // Save keys
        $privateKeyPath = $outputDir . '/private_key.pem';
        $publicKeyPath = $outputDir . '/public_key.pem';

        if (file_put_contents($privateKeyPath, $privateKeyPem) === false) {
            throw new Exception("Failed to write private key file");
        }
        
        if (file_put_contents($publicKeyPath, $publicKeyPem) === false) {
            throw new Exception("Failed to write public key file");
        }

        // Set proper permissions
        if (!chmod($privateKeyPath, 0600)) {
            throw new Exception("Failed to set private key permissions");
        }
        
        if (!chmod($publicKeyPath, 0644)) {
            throw new Exception("Failed to set public key permissions");
        }
    }

    public function loadPrivateKey(string $path): string {
        if (!file_exists($path)) {
            throw new Exception("Private key file not found: $path");
        }

        $key = file_get_contents($path);
        if ($key === false) {
            throw new Exception("Failed to read private key file: $path");
        }

        return $key;
    }

    public function loadPublicKey(string $path): string {
        if (!file_exists($path)) {
            throw new Exception("Public key file not found: $path");
        }

        $key = file_get_contents($path);
        if ($key === false) {
            throw new Exception("Failed to read public key file: $path");
        }

        return $key;
    }

    public function fetchRemoteKey(string $url): string {
        $context = stream_context_create([
            'http' => [
                'timeout' => getenv('AIHINT_TIMEOUT') ?: 30,
                'user_agent' => 'AiHint-PHP/1.0',
                'follow_location' => true,
                'max_redirects' => 3
            ]
        ]);

        $key = file_get_contents($url, false, $context);
        if ($key === false) {
            throw new Exception("Failed to fetch public key from: $url");
        }

        return $key;
    }

    public function validatePrivateKey(string $path): bool {
        try {
            $key = $this->loadPrivateKey($path);
            $pkey = openssl_pkey_get_private($key);
            if (!$pkey) {
                return false;
            }
            return true;
        } catch (Exception $e) {
            return false;
        }
    }

    public function validatePublicKey(string $path): bool {
        try {
            $key = $this->loadPublicKey($path);
            $pkey = openssl_pkey_get_public($key);
            if (!$pkey) {
                return false;
            }
            return true;
        } catch (Exception $e) {
            return false;
        }
    }
} 