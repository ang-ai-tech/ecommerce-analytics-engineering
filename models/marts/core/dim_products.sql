select
    product_id,
    product_name,
    category,
    current_unit_price,
    is_active
from {{ ref('stg_products') }}
