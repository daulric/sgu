import readline from "readline";

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

function getHCF(...numbers: number[]): number {
    if (numbers.length === 0) {
        throw new Error("At least one number is required to calculate HCF.");
    }

    const gcd = (a: number, b: number): number => {
        while (b !== 0) {
            const temp = b;
            b = a % b;
            a = temp;
        }
        return a;
    };

    return numbers.reduce((acc, num) => gcd(acc, num));
}

function getLCM(...numbers: number[]): number {
    if (numbers.length === 0) {
        throw new Error("At least one number is required to calculate LCM.");
    }

    return numbers.reduce((acc, num) => {
        return (acc * num) / getHCF(acc, num);
    })
}


function main() {
    const askQuestion = () => {
        rl.question("Enter numbers separated by commas: ", (input: string) => {
            
            if (input === "q") {
                rl.close();
                return;
            }

            const numbers = input.split(",").map(Number);
            const lcm = getLCM(...numbers);
            const hcf = getHCF(...numbers);
            console.log(`LCM: ${lcm}`);
            console.log(`HCF: ${hcf}`);
            
            askQuestion();
        });
    };

    askQuestion();
}

main();