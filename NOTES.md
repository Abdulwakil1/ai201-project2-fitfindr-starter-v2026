# Milestone 1 Notes

## Listing fields

- `id` — string
- `title` — string
- `description` — string
- `category` — string
- `style_tags` — list
- `size` — string
- `condition` — string
- `price` — float
- `colors` — list
- `brand` — string
- `platform` — string

## Wardrobe shape

A wardrobe contains an `items` list. Each item has:

- `id`
- `name`
- `category`
- `colors`
- `style_tags`
- `notes` (optional)

## Empty wardrobe

```json
{ "items": [] }
```
