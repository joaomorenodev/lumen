# Vega API — Payments

Allows you to create charges and check their status.

## Creating a charge
POST /payments with the fields:
- amount (in cents). E.g.: 1990 = $19.90.
- method: pix, boleto, or card.

The minimum amount for a charge is 100 cents ($1.00).

## Charge status
A charge goes through the statuses: pending -> paid -> settled.
It can also move to expired or refunded.

## Deadlines
- Pix: expires in 30 minutes if not paid.
- Boleto: due in 3 business days.
