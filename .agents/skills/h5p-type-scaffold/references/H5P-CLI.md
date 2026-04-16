# H5P CLI Quick Reference

The official H5P CLI provides a full development workflow for local environments and library management. Commands run relative to the current working directory.

## Installation

- npm: `npm install -g h5p-cli`
- Then use the `h5p` command.

## Local dev workflow (from h5p-cli README)

1. `h5p core`
2. `h5p setup <library>`
3. `h5p server`

The server looks for libraries relative to the folder where you run it.

## Command overview (from H5P CLI guide)

- Help: `h5p help` or `h5p help <command>`
- List libraries: `h5p list`
- Fetch libraries: `h5p get <library>`
- Check status: `h5p status [-f]`
- Commit libraries: `h5p commit <message>`
- Pack to `.h5p`: `h5p pack <library> [<library2>...] [my.h5p]`
- Version bump: `h5p increase-patch-version [<library>...]`
- Tag version: `h5p tag-version [<library>...]`
- Language files: `h5p create-language-file <library> <language-code>`
- Import language files: `h5p import-language-files <from-dir>`

If a command isn't available in your installation, run `h5p help` to see the supported commands for your version.

## References
- https://github.com/h5p/h5p-cli
- https://h5p.org/h5p-cli-guide
