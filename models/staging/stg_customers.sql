-- One row per customer: types cast, e-mails cleaned, duplicate versions removed.
with source as (
    select * from {{ source('shop', 'customers') }}
),

cleaned as (
    select
        cast(customer_id as integer)    as customer_id,
        lower(trim(email))              as email,
        upper(trim(country_code))       as country_code,
        cast(created_at as timestamp)   as created_at,
        cast(updated_at as timestamp)   as updated_at
    from source
)

select
    *,
    email like '%@{{ var("test_email_domain") }}' as is_test_account
from cleaned
-- The export can contain an older and a newer version of a customer: keep the newest.
qualify row_number() over (partition by customer_id order by updated_at desc) = 1
