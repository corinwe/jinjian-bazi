import { Astrolabe, DecadalHoroscope, MonthlyHoroscope, Plugin, YearlyHoroscope } from '../data/types';
import { EarthlyBranchName, PalaceName, StarName } from '../i18n';
import { IFunctionalStar } from '../star/FunctionalStar';
import { IFunctionalPalace } from './FunctionalPalace';
import { IFunctionalSurpalaces } from './FunctionalSurpalaces';
import { IFunctinalFlankingPalaces } from './FunctionalFlankingPalaces';
import { IFunctionalHoroscope } from './FunctionalHoroscope';
/**
 * 星盘类接口定义。
 *
 * 文档地址：https://docs.iztro.com/posts/astrolabe.html#functionalastrolabe
 */
export interface IFunctionalAstrolabe extends Astrolabe {
    /**
     * 将功能星盘转换为普通 JSON 对象
     *
     * @version 2.6.0
     */
    toJSON: () => Astrolabe;
    /**
     * 插件注入方法
     *
     * @version v2.3.0
     *
     * @param plugin 插件函数
     */
    use(plugin: Plugin): void;
    /**
     * 获取运限数据
     *
     * @version v0.2.0
     *
     * @param date 阳历日期【可选】，默认为调用时的日期
     * @param timeIndex 时辰索引【可选】，默认会自动读取当前时间的时辰
     * @returns 运限数据
     */
    horoscope: (date?: string | Date, timeIndex?: number) => IFunctionalHoroscope;
    /**
     * 获取按起运先后排列的大限列表。
     *
     * @returns 大限数据列表，第 0 项为第一个大限
     */
    decadalList: () => DecadalHoroscope[];
    /**
     * 获取指定大限内的全部流年。
     *
     * @param indexOrName 大限序号（0 为第一个大限）或者本命宫位名称
     * @returns 该大限十个虚岁对应的流年数据
     */
    yearlyList: (indexOrName: number | PalaceName) => YearlyHoroscope[];
    /**
     * 获取指定流年内的全部流月。
     *
     * @param year 流年年份，可直接传入 `yearlyList()` 返回项的 `year`
     * @param fixLeap 是否将闰月前后半月分开计算，默认为 `true`
     * @returns 该流年的流月数据；无闰月 12 项，有闰月时返回 13 或 14 项
     */
    monthlyList: (year: number, fixLeap?: boolean) => MonthlyHoroscope[];
    /**
     * 通过星耀名称获取到当前星耀的对象实例
     *
     * @version v1.2.0
     *
     * @param starName 星耀名称
     * @returns 星耀实例
     */
    star: (starName: StarName) => IFunctionalStar;
    /**
     * 获取星盘的某一个宫位
     *
     * @version v1.0.0
     *
     * @param indexOrName 宫位索引或者宫位名称
     * @returns 对应的宫位数据，若没有找到则返回undefined
     */
    palace: (indexOrName: number | PalaceName) => IFunctionalPalace | undefined;
    /**
     * 获取三方四正宫位，所谓三方四正就是传入的目标宫位，以及其对宫，财帛位和官禄位，总共四个宫位
     *
     * @version v1.1.0
     *
     * @param indexOrName 宫位索引或者宫位名称
     * @returns 三方四正宫位
     */
    surroundedPalaces: (indexOrName: number | PalaceName) => IFunctionalSurpalaces;
    /**
     * 获取目标宫位的功能夹宫对象，即目标宫位前后相邻的两个宫位。
     *
     * 返回对象的 `previous` 属性是前一宫，`next` 属性是后一宫。
     * 返回对象还提供星曜、四化分析以及 JSON 转换方法。十二宫首尾相连，
     * 因此首宫的前一宫是末宫，末宫的后一宫是首宫。
     *
     * @version 2.6.0
     *
     * @param indexOrName 目标宫位索引或者宫位名称
     * @returns 包含前一宫、后一宫及夹宫分析方法的功能夹宫对象
     */
    flankingPalaces: (indexOrName: number | PalaceName) => IFunctinalFlankingPalaces;
    /**
     *
     * 判断某一个宫位三方四正是否包含目标星耀，必须要全部包含才会返回true
     *
     * @version v1.0.0
     *
     * @param indexOrName 宫位索引或者宫位名称
     * @param stars 星耀名称数组
     * @returns true | false
     */
    isSurrounded: (indexOrName: number | PalaceName, stars: StarName[]) => boolean;
    /**
     * 判断三方四正内是否有传入星耀的其中一个，只要命中一个就会返回true
     *
     * @version v1.1.0
     * @deprecated v1.2.0
     *
     * @param indexOrName 宫位索引或者宫位名称
     * @param stars 星耀名称数组
     * @returns true | false
     */
    isSurroundedOneOf: (indexOrName: number | PalaceName, stars: StarName[]) => boolean;
    /**
     * 判断某一个宫位三方四正是否不含目标星耀，必须要全部都不在三方四正内含才会返回true
     *
     * @version v1.1.0
     * @deprecated v1.2.0
     *
     * @param indexOrName 宫位索引或者宫位名称
     * @param stars 星耀名称数组
     * @returns true | false
     */
    notSurrounded: (indexOrName: number | PalaceName, stars: StarName[]) => boolean;
}
/**
 * 星盘类。
 *
 * 文档地址：https://docs.iztro.com/posts/astrolabe.html#functionalastrolabe
 */
export default class FunctionalAstrolabe implements IFunctionalAstrolabe {
    gender: string;
    solarDate: string;
    lunarDate: string;
    chineseDate: string;
    rawDates: {
        lunarDate: import("lunar-lite/lib/types").LunarDate;
        chineseDate: import("lunar-lite/lib/types").HeavenlyStemAndEarthlyBranchDate;
    };
    time: string;
    timeRange: string;
    sign: string;
    zodiac: string;
    earthlyBranchOfSoulPalace: EarthlyBranchName;
    earthlyBranchOfBodyPalace: EarthlyBranchName;
    soul: StarName;
    body: StarName;
    fiveElementsClass: import("../i18n").FiveElementsClassName;
    palaces: IFunctionalPalace[];
    copyright: string;
    private plugins;
    constructor(data: Astrolabe);
    use(plugin: Plugin): void;
    toJSON: () => Astrolabe;
    star: (starName: StarName) => IFunctionalStar;
    horoscope: (targetDate?: string | Date, timeIndexOfTarget?: number) => IFunctionalHoroscope;
    decadalList: () => DecadalHoroscope[];
    yearlyList: (indexOrName: number | PalaceName) => YearlyHoroscope[];
    monthlyList: (year: number, fixLeap?: boolean) => MonthlyHoroscope[];
    palace: (indexOrName: number | PalaceName) => IFunctionalPalace | undefined;
    surroundedPalaces: (indexOrName: number | PalaceName) => IFunctionalSurpalaces;
    flankingPalaces: (indexOrName: number | PalaceName) => IFunctinalFlankingPalaces;
    /**
     * @deprecated 此方法已在`v1.2.0`废弃，请用下列方法替换
     *
     * @example
     *  // AS IS
     *  astrolabe.isSurrounded(0, ["紫微"]);
     *
     *  // TO BE
     *  astrolabe.surroundedPalaces(0).have(["紫微"]);
     */
    isSurrounded: (indexOrName: number | PalaceName, stars: StarName[]) => boolean;
    /**
     * @deprecated 此方法已在`v1.2.0`废弃，请用下列方法替换
     *
     * @example
     *  // AS IS
     *  astrolabe.isSurroundedOneOf(0, ["紫微"]);
     *
     *  // TO BE
     *  astrolabe.surroundedPalaces(0).haveOneOf(["紫微"]);
     */
    isSurroundedOneOf: (indexOrName: number | PalaceName, stars: StarName[]) => boolean;
    /**
     * @deprecated 此方法已在`v1.2.0`废弃，请用下列方法替换
     *
     * @example
     *  // AS IS
     *  astrolabe.notSurrounded(0, ["紫微"]);
     *
     *  // TO BE
     *  astrolabe.surroundedPalaces(0).notHave(["紫微"]);
     */
    notSurrounded: (indexOrName: number | PalaceName, stars: StarName[]) => boolean;
}
