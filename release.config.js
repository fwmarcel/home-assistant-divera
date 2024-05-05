const branch = process.env.BRANCH_NAME;

const config = {
  branches: [
    "release",
    {
      name: "develop",
      prerelease: "rc",
    },
  ],
  plugins: [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    [
      "@semantic-release/exec",
      {
        prepareCmd: "./scripts/prepare-release.sh ${nextRelease.version}",
      },
    ],
  ],
  presetConfig: {
    types: [
      {
        type: "feat",
        section: "Features :sparkles:",
      },
      {
        type: "feature",
        section: "Features :sparkles:",
      },
      {
        type: "fix",
        section: "Bug Fixes :bug:",
      },
      {
        type: "docs",
        section: "Documentation :books:",
      },
      {
        type: "refactor",
        section: "Code Refactoring :hammer:",
      },
      {
        type: "test",
        section: "Tests :umbrella:",
      },
      {
        type: "ci",
        section: "Continuous Integration :wrench:",
      },
    ],
  },
};

if (
  config.branches.some(
    (it) => it === branch || (it.name === branch && !it.prerelease),
  )
) {
  config.plugins.push(
    [
      "@semantic-release/git",
      {
        assets: ["custom_components/divera/manifest.json"],
      },
    ],
    [
      "@semantic-release/github",
      {
        assets: [
          {
            path: "custom_components/divera/divera.zip",
          },
        ],
      },
    ],
  );
} else {
  config.plugins.push([
    "@semantic-release/github",
    {
      successComment: false,
      releasedLabels: false,
      assets: [
        {
          path: "custom_components/divera/divera.zip",
        },
      ],
    },
  ]);
}

module.exports = config;
