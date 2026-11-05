-- QA test accounts must never reach reporting.
select customer_id, email
from {{ ref('dim_customers') }}
where email like '%@{{ var("test_email_domain") }}'
