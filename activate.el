(let ((virtual-env (expand-file-name "./venv")))
  (setenv "VIRTUAL_ENV" virtual-env)
  (setenv "PATH"
    (concat
      (concat virtual-env "/bin")
      ":" (getenv "PATH"))))
