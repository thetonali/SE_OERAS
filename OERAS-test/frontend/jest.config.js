const path = require('path');
const sourceRoot = path.resolve(__dirname, '../../exam-online');

module.exports = {
  rootDir: __dirname,
  testEnvironment: 'jsdom',
  testMatch: ['<rootDir>/tests/**/*.spec.js'],
  moduleFileExtensions: ['js', 'json', 'vue'],
  moduleNameMapper: {
    '^@/(.*)$': path.join(sourceRoot, 'src/$1'),
    '\\.(css|less|scss|sass)$': '<rootDir>/tests/setup/styleMock.js',
    '\\.(png|jpg|jpeg|gif|svg|ico)$': '<rootDir>/tests/setup/fileMock.js'
  },
  moduleDirectories: [
    'node_modules',
    path.resolve(__dirname, '../../exam-online/node_modules')
  ],
  transform: {
    '^.+\\.vue$': 'vue-jest',
    '^.+\\.js$': 'babel-jest'
  },
  transformIgnorePatterns: ['/node_modules/'],
  setupFilesAfterEnv: ['<rootDir>/tests/setup/testSetup.js'],
  collectCoverage: true,
  collectCoverageFrom: [
    path.join(sourceRoot, 'src/**/*.{js,vue}'),
    '!**/node_modules/**',
    '!**/main.js'
  ],
  coverageDirectory: '<rootDir>/../reports/frontend-coverage',
  coverageReporters: ['text', 'html', 'lcov', 'json-summary']
};
