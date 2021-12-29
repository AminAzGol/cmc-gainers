do $$
declare
	-- return the number of films
	rec_count int := 0;
	-- use to iterate over the film
	sym record;
	-- dynamic query
    query text;
    the_symbol text;
    for_query text;
    time_gap record;
    update_query text;
    i int;
begin
    ALTER TABLE cmc.gainers ADD COLUMN IF NOT EXISTS windw VARCHAR(50);

	query := 'select distinct symbol from cmc.gainers where windw is NULL limit 20';

	for sym in execute query using rec_count
        loop
	     the_symbol := sym.symbol;
         raise notice '%', the_symbol;

--       retrive time gaps for every symbol
	     for_query := '
	     select id, (next_date - time) as diff, symbol, time
            from ( select o.*, lead(time) over (order by time) as next_date
            from (select * from cmc.gainers where symbol = $1) o
             ) o
            where next_date > time + interval ''1 hour'';';

--         arrage data in different windows based on their time_gaps
         update_query := 'update cmc.gainers set windw= symbol || $1 where symbol=' || quote_nullable(the_symbol);
        execute update_query using '_1';
        i := 2;
        for time_gap in execute for_query using the_symbol
	         loop
                raise notice 'time gap: %', to_json(time_gap);
                execute update_query || 'and time > $2' using '_' || i, time_gap.time;
                i := i +1;
             end loop;

	end loop;
end
$$
