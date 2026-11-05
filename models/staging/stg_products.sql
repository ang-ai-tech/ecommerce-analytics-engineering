with source as (
    select * from {{ source('shop', 'products') }}
)

select
    cast(product_id as integer)         as product_id,
    trim(product_name)                  as product_name,
    trim(category)                      as category,
    cast(unit_price as decimal(10, 2))  as current_unit_price,
    lower(is_active) = 'true'           as is_active
from source
