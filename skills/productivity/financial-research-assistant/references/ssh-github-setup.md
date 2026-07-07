# SSH Key GitHub Setup Reference

## Problem: "Permission denied (publickey)"

When `git push` fails with:
```
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.
```

## Diagnosis

1. Check current keys exist:
```bash
ls -la ~/.ssh/id_* 2>/dev/null
```

2. Check if pub/priv match:
```bash
# Compare the key fingerprint
ssh-keygen -l -f ~/.ssh/id_ed25519      # private key fingerprint
ssh-keygen -l -f ~/.ssh/id_ed25519.pub  # public key fingerprint
# Must match! If not, keys are corrupted/inconsistent
```

3. Test SSH connection:
```bash
ssh -T git@github.com
# Success: "Hi corinwe! You've successfully authenticated..."
# Fail: "Permission denied (publickey)"
```

## Fix: Regenerate SSH Key

If keys don't match or were incorrectly registered:

```bash
# Backup old keys (optional)
mv ~/.ssh/id_ed25519 ~/.ssh/id_ed25519.old
mv ~/.ssh/id_ed25519.pub ~/.ssh/id_ed25519.pub.old

# Generate new key pair
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N "" -C "corin@offerpath.com"

# Show new public key to add to GitHub
cat ~/.ssh/id_ed25519.pub
```

## 🚨 Key Mismatch Error

Error message:
```
identity_sign: private key /root/.ssh/id_ed25519 contents do not match public
```

**Meaning**: The private key file and public key file are from different key pairs — they don't match. This happens when:
- Someone manually edited or replaced one file without updating the other
- Old backup keys were partially restored
- `.pub` file was copied from a different machine

**Fix**: Regenerate the key pair (command above), then add the NEW public key to GitHub. Delete the old key from GitHub first, as the old pub key won't work with the new private key.

## GitHub Setup

1. Go to GitHub → Settings → SSH and GPG keys
2. Delete old key (if exists)
3. Click "New SSH key"
4. Title: `Hermes_九九财富投资晨报` (or descriptive name)
5. Key type: `Authentication Key`
6. Paste the public key content
7. Verify after adding:
```bash
ssh -T git@github.com
```

## SSH Config (optional)

If using non-standard config, ensure `/root/.ssh/config` has:
```
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes
```
