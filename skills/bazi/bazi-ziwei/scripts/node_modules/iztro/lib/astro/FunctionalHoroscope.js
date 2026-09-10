"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var i18n_1 = require("../i18n");
var utils_1 = require("../utils");
var data_1 = require("../data");
var toJSON_1 = require("../utils/toJSON");
var _getHoroscopePalaceIndex = function ($, scope, palaceName) {
    var _a, _b;
    if (scope === 'origin') {
        return (_b = (_a = $.astrolabe.palace(palaceName)) === null || _a === void 0 ? void 0 : _a.index) !== null && _b !== void 0 ? _b : -1;
    }
    var palaceKey = (0, i18n_1.kot)(palaceName);
    return $[scope].palaceNames.findIndex(function (name) { return (0, i18n_1.kot)(name) === palaceKey; });
};
var FunctionalHoroscope = /** @class */ (function () {
    function FunctionalHoroscope(data, astrolabe) {
        var _this = this;
        this.toJSON = function () { return (0, toJSON_1.serialize)(_this); };
        this.agePalace = function () {
            return _this.astrolabe.palace(_this.age.index);
        };
        this.palace = function (palaceName, scope) {
            var targetPalaceIndex = _getHoroscopePalaceIndex(_this, scope, palaceName);
            return targetPalaceIndex < 0 ? undefined : _this.astrolabe.palace(targetPalaceIndex);
        };
        this.surroundPalaces = function (palaceName, scope) {
            var targetPalaceIndex = _getHoroscopePalaceIndex(_this, scope, palaceName);
            return targetPalaceIndex < 0 ? undefined : _this.astrolabe.surroundedPalaces(targetPalaceIndex);
        };
        this.hasHoroscopeStars = function (palaceName, scope, horoscopeStar) {
            if (!_this.decadal.stars || !_this.yearly.stars) {
                return false;
            }
            var palaceIndex = _getHoroscopePalaceIndex(_this, scope, palaceName);
            if (palaceIndex < 0) {
                return false;
            }
            var stars = (0, utils_1.mergeStars)(_this.decadal.stars, _this.yearly.stars)[palaceIndex];
            var starKeys = stars.map(function (item) { return (0, i18n_1.kot)(item.name); });
            var horoscopeStarKeys = horoscopeStar.map(function (item) { return (0, i18n_1.kot)(item); });
            return horoscopeStarKeys.every(function (star) { return starKeys.includes(star); });
        };
        this.notHaveHoroscopeStars = function (palaceName, scope, horoscopeStar) {
            if (!_this.decadal.stars || !_this.yearly.stars) {
                return false;
            }
            var palaceIndex = _getHoroscopePalaceIndex(_this, scope, palaceName);
            if (palaceIndex < 0) {
                return false;
            }
            var stars = (0, utils_1.mergeStars)(_this.decadal.stars, _this.yearly.stars)[palaceIndex];
            var starKeys = stars.map(function (item) { return (0, i18n_1.kot)(item.name); });
            var horoscopeStarKeys = horoscopeStar.map(function (item) { return (0, i18n_1.kot)(item); });
            return horoscopeStarKeys.every(function (star) { return !starKeys.includes(star); });
        };
        this.hasOneOfHoroscopeStars = function (palaceName, scope, horoscopeStar) {
            if (!_this.decadal.stars || !_this.yearly.stars) {
                return false;
            }
            var palaceIndex = _getHoroscopePalaceIndex(_this, scope, palaceName);
            if (palaceIndex < 0) {
                return false;
            }
            var stars = (0, utils_1.mergeStars)(_this.decadal.stars, _this.yearly.stars)[palaceIndex];
            var starKeys = stars.map(function (item) { return (0, i18n_1.kot)(item.name); });
            var horoscopeStarKeys = horoscopeStar.map(function (item) { return (0, i18n_1.kot)(item); });
            return horoscopeStarKeys.some(function (star) { return starKeys.includes(star); });
        };
        this.hasHoroscopeMutagen = function (palaceName, scope, horoscopeMutagen) {
            var _a, _b, _c, _d;
            if (scope === 'origin') {
                return false;
            }
            var palaceIndex = _getHoroscopePalaceIndex(_this, scope, palaceName);
            if (palaceIndex < 0) {
                return false;
            }
            var majorStars = (_b = (_a = _this.astrolabe.palace(palaceIndex)) === null || _a === void 0 ? void 0 : _a.majorStars) !== null && _b !== void 0 ? _b : [];
            var minorStars = (_d = (_c = _this.astrolabe.palace(palaceIndex)) === null || _c === void 0 ? void 0 : _c.minorStars) !== null && _d !== void 0 ? _d : [];
            var stars = (0, utils_1.mergeStars)([majorStars], [minorStars])[0].map(function (star) { return (0, i18n_1.kot)(star.name); });
            var mutagenIndex = data_1.MUTAGEN.indexOf((0, i18n_1.kot)(horoscopeMutagen));
            return stars.includes((0, i18n_1.kot)(_this[scope].mutagen[mutagenIndex]));
        };
        this.lunarDate = data.lunarDate;
        this.solarDate = data.solarDate;
        this.decadal = data.decadal;
        this.age = data.age;
        this.yearly = data.yearly;
        this.monthly = data.monthly;
        this.daily = data.daily;
        this.hourly = data.hourly;
        this.astrolabe = astrolabe;
        return this;
    }
    return FunctionalHoroscope;
}());
exports.default = FunctionalHoroscope;
