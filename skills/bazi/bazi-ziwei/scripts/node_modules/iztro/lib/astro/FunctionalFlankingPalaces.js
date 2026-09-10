"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.FunctionalFlankingPalaces = void 0;
var toJSON_1 = require("../utils/toJSON");
var analyzer_1 = require("./analyzer");
/**
 * 功能夹宫类。
 *
 * @version 2.6.0
 */
var FunctionalFlankingPalaces = /** @class */ (function () {
    function FunctionalFlankingPalaces(_a) {
        var _this = this;
        var previous = _a.previous, next = _a.next;
        this.toJSON = function () { return (0, toJSON_1.serialize)(_this); };
        this.have = function (stars) { return (0, analyzer_1.isFlankedByStars)(_this, stars); };
        this.notHave = function (stars) { return (0, analyzer_1.notFlankedByStars)(_this, stars); };
        this.haveOneOf = function (stars) { return (0, analyzer_1.isFlankedByOneOfStars)(_this, stars); };
        this.haveMutagen = function (mutagen) {
            return _this.previous.hasMutagen(mutagen) || _this.next.hasMutagen(mutagen);
        };
        this.notHaveMutagen = function (mutagen) { return !_this.haveMutagen(mutagen); };
        this.previous = previous;
        this.next = next;
    }
    return FunctionalFlankingPalaces;
}());
exports.FunctionalFlankingPalaces = FunctionalFlankingPalaces;
