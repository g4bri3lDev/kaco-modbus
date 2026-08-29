# Changelog

## [1.1.0](https://github.com/g4bri3lDev/kaco-modbus/compare/v1.0.1...v1.1.0) (2026-08-29)


### Features

* reject devices that are not KACO inverters ([5eea843](https://github.com/g4bri3lDev/kaco-modbus/commit/5eea843e8fd8ba6ebba2f417f2adda196e04c18f))


### Documentation

* add AGENTS.md ([3e38137](https://github.com/g4bri3lDev/kaco-modbus/commit/3e38137ae3459446c3105936563c2ba978ac7f3b))

## [1.0.1](https://github.com/g4bri3lDev/kaco-modbus/compare/v1.0.0...v1.0.1) (2026-08-23)


### Bug fixes

* withhold readings the inverter parks at zero while asleep ([4d162e3](https://github.com/g4bri3lDev/kaco-modbus/commit/4d162e3434261ffb6b849bda0520234312f13e27))

## [1.0.0](https://github.com/g4bri3lDev/kaco-modbus/compare/v0.1.0...v1.0.0) (2026-08-23)


### ⚠ BREAKING CHANGES

* every public name has changed. Callers of 0.1.0 need rewriting against KacoInverter rather than adapting.

### Features

* read and control KACO inverters over SunSpec Modbus ([b693e9d](https://github.com/g4bri3lDev/kaco-modbus/commit/b693e9d1bf744d8776e184859c4e1b27e5314dca))
* rebuild on modbus-connection 4.8.1 ([aa13d17](https://github.com/g4bri3lDev/kaco-modbus/commit/aa13d17f540e19a21c824db0a686b3afdc787681))
