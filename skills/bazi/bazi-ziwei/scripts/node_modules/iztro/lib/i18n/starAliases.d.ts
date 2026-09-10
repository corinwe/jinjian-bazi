/**
 * 星曜名称别名。
 *
 * 部分语言中的不同星曜具有完全相同的译名，带汉字的别名用于在反查时明确指定目标星曜。
 */
export declare const STAR_ALIASES: {
    readonly '\uCC9C\uC0C1(\u5929\u76F8)': "tianxiangMaj";
    readonly '\uCC9C\uC0C1(\u5929\u50B7)': "tianshang";
    readonly '\uCC9C\uC6D4(\u5929\u925E)': "tianyueMin";
    readonly '\uCC9C\uC6D4(\u5929\u6708)': "tianyue";
    readonly '\uAC81\uC0B4(\u52AB\u6BBA)': "jieshaAdj";
    readonly '\uAC81\uC0B4(\u52AB\u715E)': "jiesha";
    readonly '\uBE44\uB834(\u871A\u5EC9)': "feilian";
    readonly '\uBE44\uB834(\u98DB\u5EC9)': "faylian";
    readonly '\uAD00\uBD80(\u5B98\u5E9C)': "guanfu";
    readonly '\uAD00\uBD80(\u5B98\u7B26)': "gwanfu";
    readonly 'Ki\u1EBFp S\u00E1t(\u52AB\u6BBA)': "jieshaAdj";
    readonly 'Ki\u1EBFp S\u00E1t(\u52AB\u715E)': "jiesha";
    readonly 'Phi Li\u00EAm(\u871A\u5EC9)': "feilian";
    readonly 'Phi Li\u00EAm(\u98DB\u5EC9)': "faylian";
};
export type StarAlias = keyof typeof STAR_ALIASES;
