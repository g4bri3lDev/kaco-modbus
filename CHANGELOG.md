# Changelog

## [2.0.0](https://github.com/g4bri3lDev/kaco-modbus/compare/v1.1.0...v2.0.0) (2026-11-02)


### ⚠ BREAKING CHANGES

* async_set_power_limit requires revert_seconds, 1 to 65535. setpoints_held is removed. The power limit setters raise SetpointRejectedError when the inverter does not apply a write.

### Features

* add kaco-limit for supervised control tests ([5d7cf34](https://github.com/g4bri3lDev/kaco-modbus/commit/5d7cf3495ea56744227beb48985126ed3a3a2b35))
* poll immediate controls with the readings ([3ba7077](https://github.com/g4bri3lDev/kaco-modbus/commit/3ba7077378710ef61c1a4fa67542778c6e1108dd))
* take the power limit revert period from the caller ([67bc2bb](https://github.com/g4bri3lDev/kaco-modbus/commit/67bc2bb797c5aa5f295fb3557099f04ea76f031c))
* verify power limit writes and require a revert period ([7df05ae](https://github.com/g4bri3lDev/kaco-modbus/commit/7df05aeb7b2cbd81877823ea0a93414365b36117))


### Documentation

* record power limit behaviour measured on the 8.6 TL3 ([7c0cb31](https://github.com/g4bri3lDev/kaco-modbus/commit/7c0cb31884571d06ad0c619df1b05cb394a5f5f3))
* record which registers KACO allows to be written periodically ([7163239](https://github.com/g4bri3lDev/kaco-modbus/commit/7163239596dc643e05b8c4fc4eeb902c1afcd981))

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
