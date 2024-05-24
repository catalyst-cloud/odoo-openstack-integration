# OpenStack Integration Addon for Odoo v13

This is an addon to facilitate the integration between OpenStack using Adjutant and Distil with Odoo v13.

These are models and changes based on the Catalystcloud use cases, and based on how we invoice, but likely applicable in some form for other clouds running OpenStack.

## Altered Odoo Models

### Partner

We add quite a few custom fields here that link back to our models elsewhere. We also add the field `stripe_customer_id` to optional link to a customer in Stripe itself for credit card related things.

### Sale Order

The main change to Sale Order is the inclusion of `os_project` on both the Sale Order itself, and the lines. The idea here being that `os_project` on the Sale Order represents the root project for the given project group which the invoice is ultimately for, while `os_project` on each line allows each line to potentially come from a different project in that subgroup in the case of invoice grouping. We also add overrides for `_prepare_invoice` and `_prepare_invoice_line` to handle these fields.

**NOTE**: We also add `os_invoice_date` to deal with a particularly annoying issue around sale order date and how it is handled. But this will be moved to a standalone addon and renamed to `invoice_date` later.

### Account Move

Much like Sale Order, we add `os_project` to both the Account Move (invoice) and Account Move Lines. This is for the same reasons/functionality as in Sale Order.

We also have the function `is_openstack_invoice`, which works off is `os_project` is set or not.

Then there is a custom categorisation function `categorised_openstack_invoice_lines` which sorts things in a way more useful for the PDF summary page.

## Custom Models

The bulk of this addon is custom addons, many of which don't have much logic built in on the odoo side, and most of that logic (for now) is primarily handled external to Odoo in Adjutant and Distil (including the Distil Odoo Writer).

### Project

The core of this addon is built mostly around the OpenStack concept of a project, and this model is meant to represent that Odoo side. A project can only have one `owner` which is the customer partner, but then through an intermediary model called `project_contacts` has relationships to other partners such as billing contacts, etc.

Many other models link back to projects, as they are ultimately the main connection between a customer, and their OpenStack side usage.

### Customer Group

A customer group is a grouping of customers for the purposes of special discounting. The customer group is mostly for special case handling of volume discounts.

While not implemented yet, a group can also be given a pricelist which would then apply to all customers in the group.

### Voucher Code (Not used yet)

These are unused as yet, but their intended function is to allow us to create codes that can be added to an account during signup, or later, which will confer credit, or discounts as tired to the code. They would then turn into a Credit, Grant, or add a customer to a customer group. Their purpose was to be useful for a range of things.

### Credit

Credits are a model representation of credit that an OpenStack Customer has against their invoices. The balance is made up from credit transactions that are attached to the model, which gives us a history of the use of that credit.

Credits by default are not refundable, but for the purposes of prepaid or SLA credit they may have to be, and the credit_type model lets you define if a given type of credit has to be able to be refunded.

### Grant

A grant is like credit, except unlike credits, it doesn't have a balance, just a max value that can be applied to an invoice each month. It is reoccurring credit essentially.

A grant type has a special case field `only_on_group_root` that handles a case where this grant cannot be applied to any project that isn't the root of a invoice project group. This is because when grouping invoices credits/grants are applied to the whole group, and something like a dev grant should never be applied to parent projects, so a dev grant can only affect the project it is applied to or sub projects.

### Volume Discount

These are ranged of volume discount, and they are used as part of invoicing. A customer group may have it's own unique volume discounts, but by default a customer without a customer group will use the volume discounts with a group set.

### Term Discount

A model representing an agreed to term discount.

### Support Subscription (Not used, yet)

A model (and type) to represent a support subscription that a customer has signed up for of a given type.

### Reseller

We have a model for representing a reseller on our cloud, as well has what tier that reseller is at. This handles their discounts, as well as other special cases. A project is optionally linked back to a reseller.

### Trial (Not used)

A model representing a trial signup for OpenStack, and the status of that.

### Referral (Not used)

A basic referral model that would allow customers who provide referrals to earn some credit themselves.
