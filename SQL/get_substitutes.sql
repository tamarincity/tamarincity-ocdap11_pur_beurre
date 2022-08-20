-- Il faut mettre original_product.nutriscore à la place de 'd' à la ligne 18
-- Il faut remplacer 746 par original_product.id à la ligne 17

SELECT
	product_id,
	COUNT(product_id) AS weight,
	nutriscore_grade
from
	products_product p
inner join
	products_category_products
	on p.id = product_id
where
	category_id in (select cp.category_id from products_product p
				inner join products_category_products cp
					on p.id = cp.product_id
				where p.id = 746)
	and nutriscore_grade < 'd'
GROUP BY 
	product_id,
	nutriscore_grade
ORDER BY 
	weight desc,
	nutriscore_grade asc
limit 10;

