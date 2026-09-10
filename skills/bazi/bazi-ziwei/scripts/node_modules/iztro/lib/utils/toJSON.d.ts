/**
 * 将功能类实例转换为普通 JSON 对象。
 *
 * @param instance 功能类实例
 * 循环引用会被忽略，数组中的循环项会按照 JSON 规则转换为 null。
 * 转换过程不会调用嵌套对象的 toJSON 方法。
 *
 * @returns 不包含方法、循环引用和运行时引用的普通对象
 */
export declare const serialize: <T extends object>(instance: object) => T;
