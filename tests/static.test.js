// JavaScript tests for static budget manager (docs/index.html)
// Run with: node tests/static.test.js

// Import the functions from the HTML by extracting them
// Since we can't easily import from HTML, we'll replicate the logic here for testing

// ============================================================
// DECIMAL HELPERS (copied from docs/index.html)
// ============================================================

function parseAmount(amountStr) {
    if (!amountStr || !amountStr.trim()) {
        throw new Error('Montant requis');
    }
    const cleaned = amountStr.trim().replace(',', '.').replace(' ', '');
    // Check for negative sign early
    if (cleaned.startsWith('-')) {
        throw new Error('Le montant doit être positif');
    }
    const parts = cleaned.split('.');
    if (parts.length > 2) {
        throw new Error('Montant invalide');
    }
    const integerPart = parts[0] === '' ? '0' : parts[0];
    let decimalPart = parts[1] || '0';
    // Validate integer part is a valid number
    if (!/^\d+$/.test(integerPart)) {
        throw new Error('Montant invalide');
    }
    // Pad or truncate to exactly 2 digits
    if (decimalPart.length === 1) {
        decimalPart += '0';
    } else if (decimalPart.length > 2) {
        // Round half up: check 3rd digit
        const thirdDigit = parseInt(decimalPart[2], 10);
        decimalPart = decimalPart.slice(0, 2);
        if (thirdDigit >= 5) {
            // Round up
            let cents = parseInt(integerPart, 10) * 100 + parseInt(decimalPart, 10) + 1;
            return cents;
        }
    }
    if (!/^\d+$/.test(decimalPart)) {
        throw new Error('Montant invalide');
    }
    const cents = parseInt(integerPart, 10) * 100 + parseInt(decimalPart, 10);
    if (cents <= 0) {
        throw new Error('Le montant doit être positif');
    }
    return cents;
}

function formatAmount(cents) {
    if (typeof cents !== 'number' || !Number.isInteger(cents)) {
        cents = Math.round(cents * 100);
    }
    const sign = cents < 0 ? '-' : '';
    const absCents = Math.abs(cents);
    const euros = Math.floor(absCents / 100);
    const centimes = absCents % 100;
    const euroStr = String(euros).replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
    const centimeStr = String(centimes).padStart(2, '0');
    return `${sign}${euroStr},${centimeStr} €`;
}

function parseDate(dateStr) {
    const parts = dateStr.split('-');
    if (parts.length !== 3) throw new Error('Date invalide');
    return new Date(parts[0], parts[1] - 1, parts[2]);
}

function formatDate(date) {
    const d = new Date(date);
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const year = d.getFullYear();
    return `${day}/${month}/${year}`;
}

function getMonthBounds(monthStr) {
    const [year, month] = monthStr.split('-').map(Number);
    const first = new Date(year, month - 1, 1);
    const last = new Date(year, month, 0);
    return { first, last };
}

function validateDateInMonth(dateStr, monthStr) {
    const date = parseDate(dateStr);
    const { first, last } = getMonthBounds(monthStr);
    if (date < first || date > last) {
        throw new Error(`La date doit être dans le mois ${monthStr}`);
    }
    return date;
}

function getCurrentMonth() {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
}

function getPrevNextMonth(monthStr) {
    const [year, month] = monthStr.split('-').map(Number);
    let prevYear = year, prevMonth = month - 1;
    if (prevMonth === 0) { prevMonth = 12; prevYear--; }
    let nextYear = year, nextMonth = month + 1;
    if (nextMonth === 13) { nextMonth = 1; nextYear++; }
    return {
        prev: `${prevYear}-${String(prevMonth).padStart(2, '0')}`,
        next: `${nextYear}-${String(nextMonth).padStart(2, '0')}`
    };
}

// ============================================================
// TESTS
// ============================================================

let passed = 0;
let failed = 0;

function assert(condition, message) {
    if (condition) {
        console.log(`  ✓ ${message}`);
        passed++;
    } else {
        console.log(`  ✗ ${message}`);
        failed++;
    }
}

function assertThrows(fn, expectedMessage, message) {
    try {
        fn();
        console.log(`  ✗ ${message} (expected to throw)`);
        failed++;
    } catch (e) {
        if (e.message === expectedMessage || (expectedMessage && e.message.includes(expectedMessage))) {
            console.log(`  ✓ ${message}`);
            passed++;
        } else {
            console.log(`  ✗ ${message} (wrong error: ${e.message})`);
            failed++;
        }
    }
}

console.log('\n=== parseAmount tests ===');

// R8: Accept comma and dot
assert(parseAmount('12,50') === 1250, 'parseAmount("12,50") = 1250 cents');
assert(parseAmount('12.50') === 1250, 'parseAmount("12.50") = 1250 cents');
assert(parseAmount('100') === 10000, 'parseAmount("100") = 10000 cents');
assert(parseAmount('0.10') === 10, 'parseAmount("0.10") = 10 cents');
assert(parseAmount('0,10') === 10, 'parseAmount("0,10") = 10 cents');

// R8: Integer and decimal parsing
assert(parseAmount('1234.56') === 123456, 'parseAmount("1234.56") = 123456 cents');
assert(parseAmount('1234,56') === 123456, 'parseAmount("1234,56") = 123456 cents');

// R9/E2: Round half up - 2.665 should become 2.67 (267 cents)
assert(parseAmount('2.665') === 267, 'parseAmount("2.665") = 267 cents (ROUND_HALF_UP)');
assert(parseAmount('2,665') === 267, 'parseAmount("2,665") = 267 cents (ROUND_HALF_UP)');

// E1: Split 100 in three - each entry parsed correctly
assert(parseAmount('33.33') === 3333, 'parseAmount("33.33") = 3333 cents');
assert(parseAmount('33.34') === 3334, 'parseAmount("33.34") = 3334 cents');

// R11/E3/E4: Reject zero and negative
assertThrows(() => parseAmount('0'), 'Le montant doit être positif', 'parseAmount("0") throws');
assertThrows(() => parseAmount('-5'), 'Le montant doit être positif', 'parseAmount("-5") throws');
assertThrows(() => parseAmount(''), 'Montant requis', 'parseAmount("") throws');
assertThrows(() => parseAmount('abc'), 'Montant invalide', 'parseAmount("abc") throws');
assertThrows(() => parseAmount('1.2.3'), 'Montant invalide', 'parseAmount("1.2.3") throws');

console.log('\n=== formatAmount tests ===');

// R10: French formatting
assert(formatAmount(123456) === '1 234,56 €', 'formatAmount(123456) = "1 234,56 €"');
assert(formatAmount(10000) === '100,00 €', 'formatAmount(10000) = "100,00 €"');
assert(formatAmount(30) === '0,30 €', 'formatAmount(30) = "0,30 €"');
assert(formatAmount(123456789) === '1 234 567,89 €', 'formatAmount(123456789) = "1 234 567,89 €"');
assert(formatAmount(12345) === '123,45 €', 'formatAmount(12345) = "123,45 €"');

// Negative amounts
assert(formatAmount(-123456) === '-1 234,56 €', 'formatAmount(-123456) = "-1 234,56 €"');

// R9: No float errors - 0.10 * 3 = 0.30 exactly
assert(formatAmount(10 * 3) === '0,30 €', 'formatAmount(10*3) = "0,30 €" (no float error)');

// R9: 33.33 + 33.33 + 33.34 = 100.00 exactly
assert(formatAmount(3333 + 3333 + 3334) === '100,00 €', 'formatAmount(3333+3333+3334) = "100,00 €"');

// E2: 2.665 rounds to 2.67
assert(formatAmount(267) === '2,67 €', 'formatAmount(267) = "2,67 €"');

console.log('\n=== Date/Month tests ===');

// E9: Month bounds
const feb2025 = getMonthBounds('2025-02');
assert(feb2025.first.toISOString().startsWith('2025-02-01'), 'Feb 2025 first day');
assert(feb2025.last.toISOString().startsWith('2025-02-28'), 'Feb 2025 last day (non-leap)');

const feb2024 = getMonthBounds('2024-02');
assert(feb2024.last.toISOString().startsWith('2024-02-29'), 'Feb 2024 last day (leap)');

const jan2025 = getMonthBounds('2025-01');
assert(jan2025.first.toISOString().startsWith('2025-01-01'), 'Jan 2025 first day');
assert(jan2025.last.toISOString().startsWith('2025-01-31'), 'Jan 2025 last day');

const dec2025 = getMonthBounds('2025-12');
assert(dec2025.first.toISOString().startsWith('2025-12-01'), 'Dec 2025 first day');
assert(dec2025.last.toISOString().startsWith('2025-12-31'), 'Dec 2025 last day');

// E9: Prev/Next month
const prevNext = getPrevNextMonth('2025-10');
assert(prevNext.prev === '2025-09', 'Prev month from 2025-10 is 2025-09');
assert(prevNext.next === '2025-11', 'Next month from 2025-10 is 2025-11');

const prevNextJan = getPrevNextMonth('2025-01');
assert(prevNextJan.prev === '2024-12', 'Prev month from 2025-01 is 2024-12');

const prevNextDec = getPrevNextMonth('2025-12');
assert(prevNextDec.next === '2026-01', 'Next month from 2025-12 is 2026-01');

// Date validation
assertThrows(() => validateDateInMonth('2025-13-01', '2025-10'), 'La date doit être dans le mois', 'Invalid month rejected');
assertThrows(() => validateDateInMonth('2025-11-01', '2025-10'), 'La date doit être dans le mois', 'Date outside month rejected');

console.log('\n=== Integration tests ===');

// R5: Net balance calculation (income - expenses - savings)
const income = parseAmount('2500');
const expense = parseAmount('800');
const savings = parseAmount('300');
const net = income - expense - savings;
assert(formatAmount(net) === '1 400,00 €', 'Net balance: 2500 - 800 - 300 = 1400 €');

// E5: Duplicate submission guard - tested in browser, not here

// E10: CSV export format (test formatAmount output for CSV)
const csvAmount = formatAmount(123456).replace(' €', '');
assert(csvAmount === '1 234,56', 'CSV amount format correct');

console.log('\n=== Summary ===');
console.log(`Passed: ${passed}`);
console.log(`Failed: ${failed}`);
console.log(failed > 0 ? '\n❌ Some tests failed' : '\n✅ All tests passed');

process.exit(failed > 0 ? 1 : 0);