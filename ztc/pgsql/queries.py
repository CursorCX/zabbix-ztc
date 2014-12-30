#!/usr/bin/env python
""" ztc.pgsql.queries - python module for ZTC.
Stores postgresql query contsrants

Copyright (c) check_postgres.pl authors
Copyright (c) 2010 Murano Software [http://muranosoft.com/]
Copyright (c) 2011 Vladimir Rusinov <vladimir@greenmice.info>
"""

AUTOVAC_FREEZE = """SELECT
    freez,
    txns,
    ROUND(100*(txns/freez::float)) AS perc,
    datname
FROM
    (
        SELECT
            foo.freez::int,
            age(datfrozenxid) AS txns,
            datname
        FROM
            pg_database d
        JOIN
            (SELECT setting AS freez FROM pg_settings WHERE
                name = 'autovacuum_freeze_max_age') AS foo
            ON (true)
            WHERE d.datallowconn
    ) AS foo2
ORDER BY 3 DESC, 4 ASC"""

BLOAT = """SELECT
  schemaname,
  tablename,
  iname,
  reltuples::bigint,
  relpages::bigint,
  otta,
  ROUND(CASE WHEN otta=0 THEN 0.0 ELSE sml.relpages/otta::numeric END,1)
      AS tbloat,
  CASE WHEN relpages < otta THEN 0 ELSE relpages::bigint - otta END
      AS wastedpages,
  CASE WHEN relpages < otta
      THEN 0
      ELSE bs*(sml.relpages-otta)::bigint
      END AS wastedbytes,
  CASE WHEN relpages < otta
      THEN '0 bytes'::text
      ELSE (bs*(relpages-otta))::bigint || ' bytes' END AS wastedsize,
  ituples::bigint, ipages::bigint, iotta
FROM (
  SELECT
    schemaname, tablename, cc.reltuples, cc.relpages, bs,
    CEIL((cc.reltuples*((datahdr+ma-
      (CASE WHEN datahdr%ma=0
          THEN ma
          ELSE datahdr%ma
        END))+nullhdr2+4))/(bs-20::float)) AS otta,
    COALESCE(c2.relname,'?') AS iname, COALESCE(c2.reltuples,0) AS ituples,
    COALESCE(c2.relpages,0) AS ipages,
    COALESCE(CEIL((c2.reltuples*(datahdr-12))/(bs-20::float)),0)
        AS iotta -- very rough approximation, assumes all cols
  FROM (
    SELECT
      ma,bs,schemaname,tablename,
      (datawidth +
          (hdr+ma -
              (case when hdr%ma=0
                  THEN ma
                  ELSE hdr%ma
                  END)))::numeric AS datahdr,
      (maxfracsum * (nullhdr + ma - (
          case when nullhdr%ma=0
              THEN ma
              ELSE nullhdr%ma
          END))) AS nullhdr2
    FROM (
      SELECT
        schemaname, tablename, hdr, ma, bs,
        SUM((1-null_frac)*avg_width) AS datawidth,
        MAX(null_frac) AS maxfracsum,
        hdr+(
          SELECT 1+count(*)/8
          FROM pg_stats s2
          WHERE null_frac<>0 AND s2.schemaname = s.schemaname
              AND s2.tablename = s.tablename
        ) AS nullhdr
      FROM pg_stats s, (
        SELECT
          (SELECT current_setting('block_size')::numeric) AS bs,
          CASE WHEN substring(v,12,3) IN ('8.0','8.1','8.2')
              THEN 27
              ELSE 23
              END AS hdr,
          CASE WHEN v ~ 'mingw32' THEN 8 ELSE 4 END AS ma
        FROM (SELECT version() AS v) AS foo
      ) AS constants
      GROUP BY 1,2,3,4,5
    ) AS foo
  ) AS rs
  JOIN pg_class cc ON cc.relname = rs.tablename
  JOIN pg_namespace nn ON cc.relnamespace = nn.oid AND
      nn.nspname = rs.schemaname AND nn.nspname <> 'information_schema'
  LEFT JOIN pg_index i ON indrelid = cc.oid
  LEFT JOIN pg_class c2 ON c2.oid = i.indexrelid
) AS sml
"""

TNX_AGE = {
    'pre92': {
        # in 'idle_tnx' we are actually interested in knowing how long a transaction
        # is staying in idle state, that's why we measure age(now(), query_start).
        # it's a little bit wrong becuase it gives us time in idle state + duration of previous query, but
        # there's no other way to calculate it in PostgreSQL < 9.2.0
        'idle_tnx': """SELECT
                        COALESCE(EXTRACT (EPOCH FROM MAX(age(NOW(), query_start))),0) as d
                        FROM pg_stat_activity
                        WHERE current_query='<IDLE> in transaction'""",
        # in 'running' we measure how long a query is running,
        'running': """SELECT
                        COALESCE(EXTRACT (EPOCH FROM MAX(age(NOW(), query_start))),0) as d
                        FROM pg_stat_activity
                        WHERE
                            current_query<>'<IDLE> in transaction'
                            AND current_query<>'<IDLE>'
                            AND current_query NOT LIKE 'autovacuum%'
                            AND current_query NOT LIKE 'COPY%'""",
        'running_all':  """SELECT
                            COALESCE(EXTRACT (EPOCH FROM MAX(age(NOW(), query_start))),0) as d
                            FROM pg_stat_activity
                            WHERE current_query<>'<IDLE> in transaction' AND current_query<>'<IDLE>'"""
    },
    'post92': {
        # in 9.2 we have state_change column, which will give us time in idle state precisely.
        # still we use query_start to get results which are consistent with
        # pre-9.2..
        'idle_tnx': """SELECT
                        COALESCE(EXTRACT (EPOCH FROM MAX(age(NOW(), query_start))),0) as d
                        FROM pg_stat_activity
                        WHERE state LIKE 'idle in transaction%'""",
        'running': """SELECT
                        COALESCE(EXTRACT (EPOCH FROM MAX(age(NOW(), query_start))),0) as d
                        FROM pg_stat_activity
                        WHERE
                            (state='active' OR state='fastpath function call')
                            AND query NOT LIKE 'autovacuum%'
                            AND query NOT LIKE 'COPY%'""",
        'running_all':  """SELECT
                            COALESCE(EXTRACT (EPOCH FROM MAX(age(NOW(), query_start))),0) as d
                            FROM pg_stat_activity
                            WHERE state = 'active' OR state = 'fastpath function call'"""
    }
}

TNX_AGE_PREPARED = """
SELECT
    COALESCE(EXTRACT (EPOCH FROM MAX(age(NOW(), prepared))),0) as d
FROM pg_prepared_xacts
"""

# buffer queries:
BUFFER = {
    'clear': "SELECT COUNT(*) FROM pg_buffercache WHERE isdirty='f'",
    'dirty': "SELECT COUNT(*) FROM pg_buffercache WHERE isdirty='t'",
    'used': """SELECT COUNT(*) FROM pg_buffercache
                WHERE reldatabase IS NOT NULL;""",
    'total': "SELECT count(*) FROM pg_buffercache"}

# query to check if we can read pg_stat_activity properly
CHECK_INSUFF_PRIV = {
    'pre92': "SELECT 1 WHERE EXISTS (SELECT 1 FROM pg_stat_activity WHERE current_query = '<insufficient privilege>')",
    'post92': "SELECT 1 WHERE EXISTS (SELECT 1 FROM pg_stat_activity WHERE query = '<insufficient privilege>')"
}

# number of connections
CONN_NUMBER = {
    'pre92': {  # queries for PostgreSQL version < 9.2.0
        'idle_tnx': """SELECT COUNT(*) FROM pg_stat_activity
            WHERE current_query = '<IDLE> in transaction'""",
        'idle': """SELECT COUNT(*) FROM pg_stat_activity
            WHERE current_query = '<IDLE>'""",
        'total': "SELECT COUNT(*) FROM pg_stat_activity",
        'running': """SELECT COUNT(*) FROM pg_stat_activity
            WHERE current_query NOT LIKE '<IDLE%'""",
        'waiting': "SELECT COUNT(*) FROM pg_stat_activity WHERE waiting<>'f'"},
    'post92': {  # queries for PostgreSQL version >= 9.2.0
        'idle_tnx': """SELECT COUNT(*) FROM pg_stat_activity
            WHERE state LIKE 'idle in transaction%'""",
        'idle': """SELECT COUNT(*) FROM pg_stat_activity
            WHERE state = 'idle'""",
        'total': "SELECT COUNT(*) FROM pg_stat_activity",
        'running': """SELECT COUNT(*) FROM pg_stat_activity
            WHERE state = 'active' OR state = 'fastpath function call'""",
        'waiting': "SELECT COUNT(*) FROM pg_stat_activity WHERE waiting<>'f'"}
}

GET_SETTING = """SELECT setting FROM pg_settings WHERE name='%s'"""

FSM = {
    'pages': """SELECT
            pages,
            maxx,
            ROUND(100*(pages/maxx)) AS percent
        FROM
            (SELECT
                (sumrequests+numrels)*chunkpages AS pages
            FROM
                (SELECT
                    SUM(CASE WHEN avgrequest IS NULL
                        THEN interestingpages/32
                        ELSE interestingpages/16 END) AS sumrequests,
                    COUNT(relfilenode) AS numrels, 16 AS chunkpages
                FROM pg_freespacemap_relations
                ) AS foo
            ) AS foo2,
            (SELECT setting::NUMERIC AS maxx FROM pg_settings WHERE
                name = 'max_fsm_pages') AS foo3""",
    'relations': """ SELECT
            maxx,
            cur,
            ROUND(100*(cur/maxx))
        FROM (SELECT
              (SELECT COUNT(*) FROM pg_freespacemap_relations) AS cur,
              (SELECT setting::NUMERIC FROM pg_settings WHERE
              name='max_fsm_relations') AS maxx) x"""}

LOCKS = {
    'all': "SELECT COUNT(*) FROM pg_locks",
    'granted': "SELECT COUNT(*) FROM pg_locks WHERE granted='t'",
    'waiting': "SELECT COUNT(*) FROM pg_locks WHERE granted<>'t'"}

LOCKS_BY_MODE = {
    'accessexclusivelock':
    """SELECT COUNT(*) FROM pg_locks
                    WHERE mode='AccessExclusiveLock'"""}

WAL_NUMBER = """SELECT count(*) FROM pg_ls_dir('pg_xlog')
    WHERE pg_ls_dir ~ E'^[0-9A-F]{24}$'"""
