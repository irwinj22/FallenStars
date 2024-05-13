  create table
  public.a_log (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    owner integer null,
    a_id integer null,
    m_id integer null,
    type text null,
    constraint a_log_pkey primary key (id)
  ) tablespace pg_default;

  create table
  public.i_log (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    owner integer null,
    i_id integer null,
    m_id integer null,
    type text null,
    constraint i_log_pkey primary key (id)
  ) tablespace pg_default;

  create table
  public.w_log (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    w_id integer null,
    m_id integer null,
    owner integer null,
    type text null,
    constraint w_log_pkey primary key (id)
  ) tablespace pg_default;

  create table
  public.m_log (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    m_id integer null,
    attached integer null,
    type text null,
    sku text null,
    constraint m_log_pkey primary key (id)
  ) tablespace pg_default;

  create table
  public.weapon_inventory (
    id bigint generated by default as identity,
    sku text null,
    name text null,
    type text null,
    damage text null,
    price integer null default 0,
    constraint weapons_inventory_pkey primary key (id)
  ) tablespace pg_default;

  create table
  public.armor_inventory (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    sku text null,
    name text null,
    type text null,
    price integer null,
    constraint armor_inventory_pkey primary key (id)
  ) tablespace pg_default;

  create table
  public.item_inventory (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    sku text null,
    name text null,
    type text null,
    price integer null,
    constraint item_inventory_pkey primary key (id)
  ) tablespace pg_default;

  create table
  public.mod_inventory (
    id bigint generated by default as identity,
    sku text null,
    type text null,
    constraint modifierse_pkey primary key (id)
  ) tablespace pg_default;

  create table
  public.credit_ledger (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    change integer null default 0,
    constraint credit_ledger_pkey primary key (id)
  ) tablespace pg_default;

  create table
  public.rentals (
    id bigint generated by default as identity,
    checkout timestamp with time zone not null default now(),
    checkin timestamp with time zone null,
    cart_id integer null,
    rented_id integer null,
    constraint rentals_pkey primary key (id)
  ) tablespace pg_default;

  create table
  public.purchase_carts (
    id integer generated by default as identity,
    customer_name text null,
    class text null,
    level integer null,
    created_at timestamp with time zone not null default now(),
    constraint purchase_carts_pkey primary key (id)
  ) tablespace pg_default;

  create table
  public.purchase_items (
    id integer generated by default as identity,
    cart_id integer null,
    purchase_type text null,
    type_id integer null,
    quantity integer null,
    constraint purchase_items_pkey primary key (id)
  ) tablespace pg_default;

  """
  DESCRIPTIONS
  Any _log table tracks what we currently have. Each instance of an item has its own row and keeps track of who it is sold to.
  All _inventory tables desribe WHAT we want to buy, as to give guidance on our plans and modifications.
  rentals keeps track of a cart id, _log id for the thing bought, and checkin/checkout times. 
  More on mods:
    When mods are delivered, they go through the _log tables to see what has a NULL m_id value. It will then go through
    mod by mod, attaching to an item according to type.
    However, if two items share the same type, they'll be modded the same. Say you have a mace and a sword in your
    inventory and want to buy the 'sharpened' mod. You'll buy as many as the plan spits out, and then update all 'melee'
    weapons until you run out of mods. That means both the mace and the sword will be modded even though they are 
    different items, because they have the same type.

    ALSO! The plan for mods checks to see what weapons are not modded, so there is NEVER a situation where there are more
    mods than items. I didn't want to deal with it...
  More on selling:
    When a cart buys an item, the relevant _log row is updated so that the 'owner' column is the cart id.
    The same occurs when a rental happens, however, when the checkin time occurs, should set the owner back to NULL.
  """