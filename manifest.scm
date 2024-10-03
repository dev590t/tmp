;; What follows is a "manifest" equivalent to the command line you gave.
;; You can store it in a file that you may then pass to any 'guix' command
;; that accepts a '--manifest' (or '-m') option.

(concatenate-manifests
  (list (specifications->manifest
          (list "python"
                "gcc-toolchain"
                "nss"
                "nss-certs"
                "pandoc"
                "curl"
                "git" ;; for pdm add git+https://
                "python-pandas"))
        (package->development-manifest
          (specification->package "icecat"))))
