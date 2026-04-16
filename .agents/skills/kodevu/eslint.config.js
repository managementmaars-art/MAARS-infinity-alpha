export default [
  {
    ignores: [
      "node_modules/",
      "dist/",
      "coverage/",
      ".nyc_output/",
      "*.log",
      ".vscode/"
    ]
  },
  {
    files: ["**/*.js"],
    languageOptions: {
      ecmaVersion: 2023,
      sourceType: "module",
      globals: {
        node: true
      }
    },
    rules: {
      // mirror .eslintrc.json rules
      "no-unused-vars": ["warn"],
      "no-console": "off"
    },
    settings: {}
  }
];
