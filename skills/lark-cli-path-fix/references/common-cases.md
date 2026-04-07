# Common Cases

## Case 1: `zsh` works, agent shell fails

Symptoms:

- `zsh -lic 'lark-cli --version'` works
- `bash -lc 'lark-cli --version'` fails

Interpretation:

- the install is fine
- the agent shell did not load the user's interactive shell PATH

Preferred fix:

- invoke Lark commands through `zsh -lic`
- only add persistent PATH changes if repeated automation requires it

## Case 2: `lark-cli` exists, but `env: node: No such file or directory`

Symptoms:

- `which lark-cli` returns a script path
- `node` is missing in the same shell

Interpretation:

- the wrapper script is present
- its runtime is missing from PATH

Preferred fix:

- export the Node bin first
- then rerun `lark-cli --version`

## Case 3: project-local install under `.local/`

Symptoms:

- binaries exist under `.local/node-*/bin` and `.local/npm/bin`
- neither shell can find them automatically

Preferred fix:

- export both directories explicitly
- if the user wants persistence, add one PATH line to the relevant shell init file

## Case 4: real install missing

Symptoms:

- no `lark-cli` found in PATH
- no plausible project-local install found

Preferred fix:

- stop using this skill
- switch to the normal install and auth flow
