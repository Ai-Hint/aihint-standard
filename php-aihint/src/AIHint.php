<?php
namespace AIHint;

use DateTime;
use Exception;

class AIHint {
    public $target;
    public $issuer;
    public $score;
    public $method;
    public $comment;
    public $expiresAt;
    public $version = '0.1';
    public $type = 'global';
    public $issuedAt;
    public $publicKeyUrl;
    public $signature;

    public function __construct(array $data = []) {
        $this->target = $data['target'] ?? null;
        $this->issuer = $data['issuer'] ?? null;
        $this->score = $data['score'] ?? null;
        $this->method = $data['method'] ?? 'aihint-core-v1';
        $this->comment = $data['comment'] ?? null;
        $this->expiresAt = $data['expiresAt'] ?? null;
        $this->publicKeyUrl = $data['publicKeyUrl'] ?? null;
        
        if (!$this->issuedAt) {
            $this->issuedAt = new DateTime('now');
        }
        
        if (!$this->expiresAt) {
            $this->expiresAt = new DateTime('+1 year');
        }
    }

    public function sign(string $privateKeyPath): void {
        $data = $this->toArray();
        unset($data['signature']);
        
        $canonical = self::canonicalize($data);
        $privateKey = file_get_contents($privateKeyPath);
        
        if (!$privateKey) {
            throw new Exception("Failed to read private key file");
        }
        
        $pkey = openssl_pkey_get_private($privateKey);
        
        if (!$pkey) {
            $error = openssl_error_string();
            throw new Exception("Invalid private key: " . ($error ?: "Unknown error"));
        }
        
        $result = openssl_sign($canonical, $signature, $pkey, OPENSSL_ALGO_SHA256);
        
        if (!$result) {
            $error = openssl_error_string();
            throw new Exception("Failed to sign data: " . ($error ?: "Unknown error"));
        }
        
        $this->signature = base64_encode($signature);
    }

    public function verify(string $publicKeyPath = null): bool {
        if (!$this->signature) {
            return false;
        }

        $data = $this->toArray();
        $signature = base64_decode($this->signature);
        unset($data['signature']);
        $canonical = self::canonicalize($data);

        if ($publicKeyPath) {
            $publicKey = file_get_contents($publicKeyPath);
            if (!$publicKey) {
                throw new Exception("Failed to read public key file");
            }
        } else {
            // Try to fetch from public_key_url
            if ($this->publicKeyUrl) {
                $publicKey = $this->fetchRemoteKey($this->publicKeyUrl);
            } else {
                throw new Exception("No public key provided and no public_key_url available");
            }
        }

        $pkey = openssl_pkey_get_public($publicKey);
        if (!$pkey) {
            $error = openssl_error_string();
            throw new Exception("Invalid public key: " . ($error ?: "Unknown error"));
        }

        $result = openssl_verify($canonical, $signature, $pkey, OPENSSL_ALGO_SHA256);
        
        if ($result === -1) {
            $error = openssl_error_string();
            throw new Exception("Verification error: " . ($error ?: "Unknown error"));
        }
        
        return $result === 1;
    }

    public function validate(): bool {
        $required = ["version", "type", "target", "issuer", "score", "method", "issued_at", "expires_at"];
        $data = $this->toArray();
        
        foreach ($required as $key) {
            if (!array_key_exists($key, $data) || empty($data[$key])) {
                return false;
            }
        }

        // Validate score range
        if ($this->score < 0.0 || $this->score > 1.0) {
            return false;
        }

        // Validate dates
        if ($this->expiresAt <= $this->issuedAt) {
            return false;
        }

        return true;
    }

    public function save(string $filePath): void {
        $data = $this->toArray();
        file_put_contents($filePath, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES));
    }

    public function load(string $filePath): void {
        $json = file_get_contents($filePath);
        $data = json_decode($json, true);
        
        if (!$data) {
            throw new Exception("Invalid JSON file");
        }

        $this->target = $data['target'] ?? null;
        $this->issuer = $data['issuer'] ?? null;
        $this->score = $data['score'] ?? null;
        $this->method = $data['method'] ?? 'aihint-core-v1';
        $this->comment = $data['comment'] ?? null;
        $this->publicKeyUrl = $data['public_key_url'] ?? null;
        $this->signature = $data['signature'] ?? null;
        $this->version = $data['version'] ?? '0.1';
        $this->type = $data['type'] ?? 'global';
        
        $this->issuedAt = new DateTime($data['issued_at']);
        $this->expiresAt = new DateTime($data['expires_at']);
    }

    public static function fromUrl(string $url): AIHint {
        $json = file_get_contents($url);
        if (!$json) {
            throw new Exception("Failed to fetch from URL: $url");
        }

        $data = json_decode($json, true);
        if (!$data) {
            throw new Exception("Invalid JSON from URL");
        }

        $aihint = new AIHint();
        $aihint->loadFromArray($data);
        return $aihint;
    }

    public function toArray(): array {
        return [
            'version' => $this->version,
            'type' => $this->type,
            'target' => $this->target,
            'issuer' => $this->issuer,
            'score' => $this->score,
            'method' => $this->method,
            'issued_at' => $this->issuedAt->format('c'),
            'expires_at' => $this->expiresAt->format('c'),
            'public_key_url' => $this->publicKeyUrl,
            'comment' => $this->comment,
            'signature' => $this->signature
        ];
    }

    private function loadFromArray(array $data): void {
        $this->target = $data['target'] ?? null;
        $this->issuer = $data['issuer'] ?? null;
        $this->score = $data['score'] ?? null;
        $this->method = $data['method'] ?? 'aihint-core-v1';
        $this->comment = $data['comment'] ?? null;
        $this->publicKeyUrl = $data['public_key_url'] ?? null;
        $this->signature = $data['signature'] ?? null;
        $this->version = $data['version'] ?? '0.1';
        $this->type = $data['type'] ?? 'global';
        
        $this->issuedAt = new DateTime($data['issued_at']);
        $this->expiresAt = new DateTime($data['expires_at']);
    }

    private function fetchRemoteKey(string $url): string {
        $context = stream_context_create([
            'http' => [
                'timeout' => getenv('AIHINT_TIMEOUT') ?: 30,
                'user_agent' => 'AiHint-PHP/1.0'
            ]
        ]);

        $key = file_get_contents($url, false, $context);
        if (!$key) {
            throw new Exception("Failed to fetch public key from: $url");
        }

        return $key;
    }

    public static function canonicalize(array $data): string {
        ksort($data);
        return json_encode($data, JSON_UNESCAPED_SLASHES);
    }

    // Static methods for backward compatibility
    public static function signHint(array $hint, string $privateKeyPath): array {
        $aihint = new AIHint($hint);
        $aihint->sign($privateKeyPath);
        return $aihint->toArray();
    }

    public static function verifyHint(array $hint, string $publicKeyPath): bool {
        $aihint = new AIHint($hint);
        return $aihint->verify($publicKeyPath);
    }

    public static function validateHint(array $hint): bool {
        $aihint = new AIHint($hint);
        return $aihint->validate();
    }
}
