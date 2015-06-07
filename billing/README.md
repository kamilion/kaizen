This Kaizen plugin deals with handling billing and transactions.

There are several sub-plugins available, implimenting a standard STRIPE.JS style interface.

This interface is based on passing a single integer containing the number of pennies to charge the customer.

The Product model will describe a single transaction.
This is useful for selling individual products with addon items using a shopping cart.

The Service model will describe a recurring transaction.
This is useful for microtransactions like online games, virtual hosting, or recurring donators.

The Addon model will describe an addition to the transaction's amount.
The root model for Addon will determine how an addition applies to it's root object.