function getProportion(value: number, ...ratios: number[]): number[] {
    if (ratios.length === 0) {
        throw new Error("At least one ratio is required to calculate proportion.");
    }

    if (!value || value === 0) {
        throw new Error("Value must be a non-zero number to calculate proportion.");
    }

    const sum = ratios.reduce((acc, num) => acc + num, 0);

    if (sum === 0) {
        throw new Error("The sum of ratios cannot be zero.");
    }

    const part_1 = value / sum;

    const returnArr = [];
    
    for (const ratio of ratios) {
        returnArr.push(part_1 * ratio);
    }


    return returnArr;
}

console.log(getProportion(100, 1,4,5))