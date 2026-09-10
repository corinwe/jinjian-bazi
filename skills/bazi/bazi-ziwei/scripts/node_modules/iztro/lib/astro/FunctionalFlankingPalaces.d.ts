import { FlankingPalaces } from '../data/types';
import { Mutagen, StarName } from '../i18n';
/**
 * 功能夹宫接口。
 *
 * @version 2.6.0
 */
export interface IFunctinalFlankingPalaces extends FlankingPalaces {
    /**
     * 将功能夹宫转换为普通 JSON 对象。
     *
     * @version 2.6.0
     */
    toJSON: () => FlankingPalaces;
    /**
     * 判断两个夹宫内是否包含全部目标星曜。
     *
     * @version 2.6.0
     *
     * @param stars 星曜名称，可以包含主星、辅星、杂曜
     * @returns 两个夹宫合计包含全部目标星曜时返回 true
     */
    have: (stars: StarName[]) => boolean;
    /**
     * 判断两个夹宫内是否完全不包含目标星曜。
     *
     * @version 2.6.0
     *
     * @param stars 星曜名称，可以包含主星、辅星、杂曜
     * @returns 两个夹宫均不包含任何目标星曜时返回 true
     */
    notHave: (stars: StarName[]) => boolean;
    /**
     * 判断两个夹宫内是否包含任意一颗目标星曜。
     *
     * @version 2.6.0
     *
     * @param stars 星曜名称，可以包含主星、辅星、杂曜
     * @returns 任意一个夹宫包含任意一颗目标星曜时返回 true
     */
    haveOneOf: (stars: StarName[]) => boolean;
    /**
     * 判断两个夹宫内是否存在指定四化。
     *
     * @version 2.6.0
     *
     * @param mutagen 四化名称【禄｜权｜科｜忌】
     * @returns 任意一个夹宫存在指定四化时返回 true
     */
    haveMutagen: (mutagen: Mutagen) => boolean;
    /**
     * 判断两个夹宫内是否不存在指定四化。
     *
     * @version 2.6.0
     *
     * @param mutagen 四化名称【禄｜权｜科｜忌】
     * @returns 两个夹宫均不存在指定四化时返回 true
     */
    notHaveMutagen: (mutagen: Mutagen) => boolean;
}
/**
 * 功能夹宫类。
 *
 * @version 2.6.0
 */
export declare class FunctionalFlankingPalaces implements IFunctinalFlankingPalaces {
    previous: import("./FunctionalPalace").IFunctionalPalace;
    next: import("./FunctionalPalace").IFunctionalPalace;
    constructor({ previous, next }: FlankingPalaces);
    toJSON: () => FlankingPalaces;
    have: (stars: StarName[]) => boolean;
    notHave: (stars: StarName[]) => boolean;
    haveOneOf: (stars: StarName[]) => boolean;
    haveMutagen: (mutagen: Mutagen) => boolean;
    notHaveMutagen: (mutagen: Mutagen) => boolean;
}
