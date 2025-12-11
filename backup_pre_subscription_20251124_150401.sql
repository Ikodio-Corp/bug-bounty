--
-- PostgreSQL database dump
--

\restrict vURxlRZzOxGQEigwI2uLsOPkPXJqvPbnfTS4FD2spTkvtZkHnVBr6OORdRE0xY1

-- Dumped from database version 14.20 (Homebrew)
-- Dumped by pg_dump version 14.20 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: automationjobstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.automationjobstatus AS ENUM (
    'PENDING',
    'RUNNING',
    'COMPLETED',
    'FAILED',
    'CANCELLED'
);


ALTER TYPE public.automationjobstatus OWNER TO postgres;

--
-- Name: bugseverity; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.bugseverity AS ENUM (
    'CRITICAL',
    'HIGH',
    'MEDIUM',
    'LOW',
    'INFO'
);


ALTER TYPE public.bugseverity OWNER TO postgres;

--
-- Name: bugstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.bugstatus AS ENUM (
    'DISCOVERED',
    'VALIDATING',
    'VALIDATED',
    'REPORTED',
    'TRIAGED',
    'FIXED',
    'ACCEPTED',
    'REJECTED',
    'DUPLICATE',
    'PAID'
);


ALTER TYPE public.bugstatus OWNER TO postgres;

--
-- Name: bugtype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.bugtype AS ENUM (
    'SQL_INJECTION',
    'XSS',
    'CSRF',
    'SSRF',
    'XXE',
    'IDOR',
    'AUTH_BYPASS',
    'BUSINESS_LOGIC',
    'RCE',
    'LFI',
    'RFI',
    'DESERIALIZATION',
    'API_SECURITY',
    'GRAPHQL',
    'OAUTH',
    'JWT',
    'CLOUD_MISCONFIGURATION',
    'CONTAINER_ESCAPE',
    'OTHER'
);


ALTER TYPE public.bugtype OWNER TO postgres;

--
-- Name: fixstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.fixstatus AS ENUM (
    'PENDING',
    'ACCEPTED',
    'IN_PROGRESS',
    'COMPLETED',
    'VERIFIED',
    'REJECTED',
    'DISPUTED'
);


ALTER TYPE public.fixstatus OWNER TO postgres;

--
-- Name: guildmembershiptier; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.guildmembershiptier AS ENUM (
    'APPRENTICE',
    'JOURNEYMAN',
    'MASTER',
    'GRANDMASTER'
);


ALTER TYPE public.guildmembershiptier OWNER TO postgres;

--
-- Name: insuranceclaimstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.insuranceclaimstatus AS ENUM (
    'SUBMITTED',
    'UNDER_REVIEW',
    'APPROVED',
    'REJECTED',
    'PAID'
);


ALTER TYPE public.insuranceclaimstatus OWNER TO postgres;

--
-- Name: insurancepolicystatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.insurancepolicystatus AS ENUM (
    'ACTIVE',
    'EXPIRED',
    'CANCELLED',
    'PENDING'
);


ALTER TYPE public.insurancepolicystatus OWNER TO postgres;

--
-- Name: marketplacelistingstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.marketplacelistingstatus AS ENUM (
    'ACTIVE',
    'SOLD',
    'CANCELLED',
    'PENDING_VERIFICATION'
);


ALTER TYPE public.marketplacelistingstatus OWNER TO postgres;

--
-- Name: paymentstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.paymentstatus AS ENUM (
    'PENDING',
    'PROCESSING',
    'COMPLETED',
    'FAILED',
    'REFUNDED'
);


ALTER TYPE public.paymentstatus OWNER TO postgres;

--
-- Name: proposalstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.proposalstatus AS ENUM (
    'DRAFT',
    'ACTIVE',
    'PASSED',
    'REJECTED',
    'EXECUTED',
    'CANCELLED'
);


ALTER TYPE public.proposalstatus OWNER TO postgres;

--
-- Name: subscriptiontier; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.subscriptiontier AS ENUM (
    'FREE',
    'BRONZE',
    'SILVER',
    'GOLD',
    'PLATINUM'
);


ALTER TYPE public.subscriptiontier OWNER TO postgres;

--
-- Name: userrole; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.userrole AS ENUM (
    'ADMIN',
    'HUNTER',
    'DEVELOPER',
    'COMPANY',
    'UNIVERSITY',
    'RESEARCHER',
    'INVESTOR'
);


ALTER TYPE public.userrole OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: agi_research_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.agi_research_logs (
    id integer NOT NULL,
    experiment_name character varying(255) NOT NULL,
    experiment_type character varying(100),
    model_architecture character varying(255),
    model_parameters json,
    training_data_size integer,
    training_duration integer,
    performance_metrics json,
    bugs_discovered integer,
    novel_vulnerabilities integer,
    success_rate double precision,
    false_positive_rate double precision,
    insights text,
    limitations text,
    next_steps text,
    budget_used double precision,
    created_at timestamp without time zone
);


ALTER TABLE public.agi_research_logs OWNER TO postgres;

--
-- Name: agi_research_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.agi_research_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.agi_research_logs_id_seq OWNER TO postgres;

--
-- Name: agi_research_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.agi_research_logs_id_seq OWNED BY public.agi_research_logs.id;


--
-- Name: bci_security_audits; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bci_security_audits (
    id integer NOT NULL,
    device_manufacturer character varying(255) NOT NULL,
    device_model character varying(255) NOT NULL,
    firmware_version character varying(100),
    audit_type character varying(100),
    vulnerabilities_found json,
    neural_data_privacy_score double precision,
    device_security_score double precision,
    authentication_score double precision,
    recommendations json,
    audit_date timestamp without time zone NOT NULL,
    auditor_id integer,
    report_url character varying(500),
    is_confidential boolean,
    created_at timestamp without time zone
);


ALTER TABLE public.bci_security_audits OWNER TO postgres;

--
-- Name: bci_security_audits_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bci_security_audits_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.bci_security_audits_id_seq OWNER TO postgres;

--
-- Name: bci_security_audits_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bci_security_audits_id_seq OWNED BY public.bci_security_audits.id;


--
-- Name: bug_derivatives; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bug_derivatives (
    id integer NOT NULL,
    derivative_type character varying(50) NOT NULL,
    underlying_asset character varying(255) NOT NULL,
    prediction text NOT NULL,
    confidence_percentage double precision NOT NULL,
    strike_condition text,
    expiry_date timestamp without time zone NOT NULL,
    premium double precision NOT NULL,
    payout double precision NOT NULL,
    seller_id integer NOT NULL,
    buyer_id integer,
    status character varying(50),
    outcome character varying(50),
    settled_at timestamp without time zone,
    created_at timestamp without time zone
);


ALTER TABLE public.bug_derivatives OWNER TO postgres;

--
-- Name: bug_derivatives_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bug_derivatives_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.bug_derivatives_id_seq OWNER TO postgres;

--
-- Name: bug_derivatives_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bug_derivatives_id_seq OWNED BY public.bug_derivatives.id;


--
-- Name: bug_future_positions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bug_future_positions (
    id integer NOT NULL,
    future_id integer NOT NULL,
    user_id integer NOT NULL,
    position_type character varying(10) NOT NULL,
    quantity integer NOT NULL,
    entry_price double precision NOT NULL,
    current_value double precision,
    unrealized_pnl double precision,
    status character varying(50),
    opened_at timestamp without time zone,
    closed_at timestamp without time zone,
    realized_pnl double precision
);


ALTER TABLE public.bug_future_positions OWNER TO postgres;

--
-- Name: bug_future_positions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bug_future_positions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.bug_future_positions_id_seq OWNER TO postgres;

--
-- Name: bug_future_positions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bug_future_positions_id_seq OWNED BY public.bug_future_positions.id;


--
-- Name: bug_futures_extended; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bug_futures_extended (
    id integer NOT NULL,
    contract_name character varying(255) NOT NULL,
    target_company character varying(255),
    target_technology character varying(255),
    vulnerability_type character varying(100),
    contract_price double precision NOT NULL,
    payout_condition text,
    expiration_date timestamp without time zone NOT NULL,
    status character varying(50),
    creator_id integer NOT NULL,
    total_contracts_issued integer,
    total_contracts_traded integer,
    created_at timestamp without time zone
);


ALTER TABLE public.bug_futures_extended OWNER TO postgres;

--
-- Name: bug_futures_extended_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bug_futures_extended_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.bug_futures_extended_id_seq OWNER TO postgres;

--
-- Name: bug_futures_extended_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bug_futures_extended_id_seq OWNED BY public.bug_futures_extended.id;


--
-- Name: bug_futures_old; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bug_futures_old (
    id integer NOT NULL,
    buyer_id integer NOT NULL,
    target_company character varying(255) NOT NULL,
    target_domain character varying(255) NOT NULL,
    requested_severity public.bugseverity,
    requested_types json,
    budget double precision NOT NULL,
    deadline timestamp without time zone NOT NULL,
    requirements text,
    special_instructions text,
    status character varying(50),
    assigned_hunter_id integer,
    assigned_at timestamp without time zone,
    completed_at timestamp without time zone,
    bug_id integer,
    created_at timestamp without time zone
);


ALTER TABLE public.bug_futures_old OWNER TO postgres;

--
-- Name: bug_futures_old_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bug_futures_old_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.bug_futures_old_id_seq OWNER TO postgres;

--
-- Name: bug_futures_old_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bug_futures_old_id_seq OWNED BY public.bug_futures_old.id;


--
-- Name: bug_index_funds; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bug_index_funds (
    id integer NOT NULL,
    fund_name character varying(255) NOT NULL,
    fund_symbol character varying(10) NOT NULL,
    description text,
    strategy text,
    total_value double precision,
    shares_outstanding integer,
    nav_per_share double precision,
    bug_portfolio json,
    industry_allocation json,
    severity_allocation json,
    ytd_return double precision,
    inception_return double precision,
    management_fee double precision,
    performance_fee double precision,
    minimum_investment double precision,
    investors json,
    is_active boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.bug_index_funds OWNER TO postgres;

--
-- Name: bug_index_funds_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bug_index_funds_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.bug_index_funds_id_seq OWNER TO postgres;

--
-- Name: bug_index_funds_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bug_index_funds_id_seq OWNED BY public.bug_index_funds.id;


--
-- Name: bug_marketplace_listings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bug_marketplace_listings (
    id integer NOT NULL,
    bug_id integer NOT NULL,
    seller_id integer NOT NULL,
    listing_price double precision NOT NULL,
    instant_payment_percentage double precision,
    original_bounty_amount double precision,
    status public.marketplacelistingstatus,
    verification_status character varying(50),
    verified_at timestamp without time zone,
    listing_type character varying(50),
    description text,
    listed_at timestamp without time zone,
    sold_at timestamp without time zone,
    views_count integer,
    created_at timestamp without time zone
);


ALTER TABLE public.bug_marketplace_listings OWNER TO postgres;

--
-- Name: bug_marketplace_listings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bug_marketplace_listings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.bug_marketplace_listings_id_seq OWNER TO postgres;

--
-- Name: bug_marketplace_listings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bug_marketplace_listings_id_seq OWNED BY public.bug_marketplace_listings.id;


--
-- Name: bug_marketplace_trades; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bug_marketplace_trades (
    id integer NOT NULL,
    listing_id integer NOT NULL,
    buyer_id integer NOT NULL,
    seller_id integer NOT NULL,
    trade_price double precision NOT NULL,
    platform_fee double precision,
    seller_receives double precision,
    trade_status character varying(50),
    payment_method character varying(50),
    payment_reference character varying(255),
    escrow_released boolean,
    escrow_released_at timestamp without time zone,
    traded_at timestamp without time zone,
    completed_at timestamp without time zone,
    created_at timestamp without time zone
);


ALTER TABLE public.bug_marketplace_trades OWNER TO postgres;

--
-- Name: bug_marketplace_trades_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bug_marketplace_trades_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.bug_marketplace_trades_id_seq OWNER TO postgres;

--
-- Name: bug_marketplace_trades_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bug_marketplace_trades_id_seq OWNED BY public.bug_marketplace_trades.id;


--
-- Name: bug_nfts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bug_nfts (
    id integer NOT NULL,
    bug_id integer NOT NULL,
    owner_id integer NOT NULL,
    token_id character varying(255) NOT NULL,
    contract_address character varying(255) NOT NULL,
    blockchain character varying(50),
    metadata_uri character varying(500),
    nft_metadata json,
    mint_price double precision,
    current_price double precision,
    royalty_percentage double precision,
    is_listed boolean,
    listing_price double precision,
    transaction_history json,
    minted_at timestamp without time zone NOT NULL,
    created_at timestamp without time zone
);


ALTER TABLE public.bug_nfts OWNER TO postgres;

--
-- Name: bug_nfts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bug_nfts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.bug_nfts_id_seq OWNER TO postgres;

--
-- Name: bug_nfts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bug_nfts_id_seq OWNED BY public.bug_nfts.id;


--
-- Name: bugs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bugs (
    id integer NOT NULL,
    hunter_id integer NOT NULL,
    scan_id integer,
    title character varying(500) NOT NULL,
    description text NOT NULL,
    bug_type public.bugtype NOT NULL,
    severity public.bugseverity NOT NULL,
    status public.bugstatus NOT NULL,
    cvss_score double precision,
    cwe_id character varying(50),
    target_url character varying(1000) NOT NULL,
    target_domain character varying(255) NOT NULL,
    endpoint character varying(1000),
    parameter character varying(255),
    steps_to_reproduce text,
    proof_of_concept text,
    impact text,
    remediation text,
    exploit_code text,
    payload text,
    screenshots json,
    video_url character varying(500),
    attachments json,
    platform_name character varying(100),
    platform_program_id character varying(255),
    platform_report_id character varying(255),
    is_chain boolean,
    chain_bugs json,
    chain_description text,
    discovery_time_seconds integer,
    ai_generated boolean,
    ai_confidence double precision,
    bounty_amount double precision,
    bounty_currency character varying(10),
    private_sale boolean,
    private_sale_amount double precision,
    reported_at timestamp without time zone,
    accepted_at timestamp without time zone,
    fixed_at timestamp without time zone,
    paid_at timestamp without time zone,
    is_public boolean,
    disclosure_date timestamp without time zone,
    tags json,
    bug_metadata json,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.bugs OWNER TO postgres;

--
-- Name: bugs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bugs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.bugs_id_seq OWNER TO postgres;

--
-- Name: bugs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bugs_id_seq OWNED BY public.bugs.id;


--
-- Name: comments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.comments (
    id integer NOT NULL,
    post_id integer NOT NULL,
    user_id integer NOT NULL,
    content text NOT NULL,
    parent_comment_id integer,
    likes_count integer,
    created_at timestamp without time zone
);


ALTER TABLE public.comments OWNER TO postgres;

--
-- Name: comments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.comments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.comments_id_seq OWNER TO postgres;

--
-- Name: comments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.comments_id_seq OWNED BY public.comments.id;


--
-- Name: cost_optimization_recommendations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cost_optimization_recommendations (
    id integer NOT NULL,
    company_id integer NOT NULL,
    resource_id integer,
    recommendation_type character varying(100) NOT NULL,
    current_cost_monthly double precision NOT NULL,
    projected_cost_monthly double precision NOT NULL,
    savings_monthly double precision NOT NULL,
    savings_percentage double precision,
    recommendation_details text NOT NULL,
    action_required text,
    priority character varying(50),
    status character varying(50),
    implemented_at timestamp without time zone,
    actual_savings_monthly double precision,
    created_at timestamp without time zone
);


ALTER TABLE public.cost_optimization_recommendations OWNER TO postgres;

--
-- Name: cost_optimization_recommendations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cost_optimization_recommendations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cost_optimization_recommendations_id_seq OWNER TO postgres;

--
-- Name: cost_optimization_recommendations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cost_optimization_recommendations_id_seq OWNED BY public.cost_optimization_recommendations.id;


--
-- Name: courses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.courses (
    id integer NOT NULL,
    instructor_id integer NOT NULL,
    title character varying(500) NOT NULL,
    description text,
    category character varying(100),
    difficulty character varying(50),
    price double precision NOT NULL,
    curriculum json,
    enrolled_count integer,
    completed_count integer,
    rating double precision,
    reviews_count integer,
    video_urls json,
    resources json,
    is_published boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.courses OWNER TO postgres;

--
-- Name: courses_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.courses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.courses_id_seq OWNER TO postgres;

--
-- Name: courses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.courses_id_seq OWNED BY public.courses.id;


--
-- Name: creator_subscriptions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.creator_subscriptions (
    id integer NOT NULL,
    creator_id integer NOT NULL,
    subscriber_id integer NOT NULL,
    tier character varying(50) NOT NULL,
    monthly_price double precision NOT NULL,
    benefits json,
    status character varying(50),
    started_at timestamp without time zone NOT NULL,
    next_billing_date timestamp without time zone,
    created_at timestamp without time zone
);


ALTER TABLE public.creator_subscriptions OWNER TO postgres;

--
-- Name: creator_subscriptions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.creator_subscriptions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.creator_subscriptions_id_seq OWNER TO postgres;

--
-- Name: creator_subscriptions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.creator_subscriptions_id_seq OWNED BY public.creator_subscriptions.id;


--
-- Name: dao_governance_extended; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dao_governance_extended (
    id integer NOT NULL,
    dao_name character varying(255) NOT NULL,
    total_token_supply double precision,
    circulating_supply double precision,
    governance_token_symbol character varying(10),
    treasury_balance double precision,
    min_proposal_tokens double precision,
    voting_period_hours integer,
    quorum_percentage double precision,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.dao_governance_extended OWNER TO postgres;

--
-- Name: dao_governance_extended_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dao_governance_extended_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dao_governance_extended_id_seq OWNER TO postgres;

--
-- Name: dao_governance_extended_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dao_governance_extended_id_seq OWNED BY public.dao_governance_extended.id;


--
-- Name: dao_governance_old; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dao_governance_old (
    id integer NOT NULL,
    token_symbol character varying(10) NOT NULL,
    token_name character varying(100) NOT NULL,
    total_supply double precision NOT NULL,
    circulating_supply double precision,
    token_price double precision,
    market_cap double precision,
    treasury_balance double precision,
    treasury_assets json,
    bug_portfolio_value double precision,
    total_holders integer,
    governance_proposals json,
    revenue_30d double precision,
    revenue_ytd double precision,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.dao_governance_old OWNER TO postgres;

--
-- Name: dao_governance_old_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dao_governance_old_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dao_governance_old_id_seq OWNER TO postgres;

--
-- Name: dao_governance_old_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dao_governance_old_id_seq OWNED BY public.dao_governance_old.id;


--
-- Name: dao_proposals; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dao_proposals (
    id integer NOT NULL,
    proposal_number character varying(50),
    title character varying(500) NOT NULL,
    description text NOT NULL,
    proposer_id integer NOT NULL,
    proposal_type character varying(100),
    status public.proposalstatus,
    voting_starts_at timestamp without time zone,
    voting_ends_at timestamp without time zone,
    votes_for double precision,
    votes_against double precision,
    votes_abstain double precision,
    total_voting_power double precision,
    quorum_reached boolean,
    execution_data json,
    executed_at timestamp without time zone,
    executed_by integer,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.dao_proposals OWNER TO postgres;

--
-- Name: dao_proposals_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dao_proposals_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dao_proposals_id_seq OWNER TO postgres;

--
-- Name: dao_proposals_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dao_proposals_id_seq OWNED BY public.dao_proposals.id;


--
-- Name: dao_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dao_tokens (
    id integer NOT NULL,
    user_id integer NOT NULL,
    token_balance double precision,
    staked_balance double precision,
    earned_from_bug_bounties double precision,
    earned_from_marketplace double precision,
    earned_from_governance double precision,
    voting_power double precision,
    last_updated timestamp without time zone,
    created_at timestamp without time zone
);


ALTER TABLE public.dao_tokens OWNER TO postgres;

--
-- Name: dao_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dao_tokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dao_tokens_id_seq OWNER TO postgres;

--
-- Name: dao_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dao_tokens_id_seq OWNED BY public.dao_tokens.id;


--
-- Name: dao_treasury_transactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dao_treasury_transactions (
    id integer NOT NULL,
    transaction_type character varying(50) NOT NULL,
    amount double precision NOT NULL,
    from_address character varying(255),
    to_address character varying(255),
    purpose text,
    proposal_id integer,
    transaction_hash character varying(255),
    executed_at timestamp without time zone
);


ALTER TABLE public.dao_treasury_transactions OWNER TO postgres;

--
-- Name: dao_treasury_transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dao_treasury_transactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dao_treasury_transactions_id_seq OWNER TO postgres;

--
-- Name: dao_treasury_transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dao_treasury_transactions_id_seq OWNED BY public.dao_treasury_transactions.id;


--
-- Name: dao_votes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dao_votes (
    id integer NOT NULL,
    proposal_id integer NOT NULL,
    voter_id integer NOT NULL,
    vote_choice character varying(20) NOT NULL,
    voting_power double precision NOT NULL,
    reason text,
    voted_at timestamp without time zone
);


ALTER TABLE public.dao_votes OWNER TO postgres;

--
-- Name: dao_votes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dao_votes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dao_votes_id_seq OWNER TO postgres;

--
-- Name: dao_votes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dao_votes_id_seq OWNED BY public.dao_votes.id;


--
-- Name: deployment_executions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.deployment_executions (
    id integer NOT NULL,
    pipeline_id integer NOT NULL,
    deployment_number character varying(50),
    commit_hash character varying(255),
    commit_message text,
    triggered_by integer,
    triggered_by_ai boolean,
    environment character varying(100),
    status character varying(50),
    stages_completed json,
    started_at timestamp without time zone,
    completed_at timestamp without time zone,
    duration_seconds integer,
    logs_url character varying(1000),
    rollback_executed boolean,
    created_at timestamp without time zone
);


ALTER TABLE public.deployment_executions OWNER TO postgres;

--
-- Name: deployment_executions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.deployment_executions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.deployment_executions_id_seq OWNER TO postgres;

--
-- Name: deployment_executions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.deployment_executions_id_seq OWNED BY public.deployment_executions.id;


--
-- Name: deployment_pipelines; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.deployment_pipelines (
    id integer NOT NULL,
    pipeline_name character varying(255) NOT NULL,
    company_id integer NOT NULL,
    repository_url character varying(1000),
    branch character varying(255),
    pipeline_config json,
    stages json,
    auto_deploy boolean,
    last_deployment_id integer,
    last_deployment_status character varying(50),
    success_rate double precision,
    average_duration_minutes double precision,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.deployment_pipelines OWNER TO postgres;

--
-- Name: deployment_pipelines_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.deployment_pipelines_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.deployment_pipelines_id_seq OWNER TO postgres;

--
-- Name: deployment_pipelines_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.deployment_pipelines_id_seq OWNED BY public.deployment_pipelines.id;


--
-- Name: devops_automation_jobs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.devops_automation_jobs (
    id integer NOT NULL,
    job_type character varying(100) NOT NULL,
    company_id integer NOT NULL,
    status public.automationjobstatus,
    configuration json,
    target_environment character varying(100),
    target_region character varying(100),
    estimated_duration_minutes integer,
    actual_duration_minutes integer,
    resources_created json,
    cost_estimate double precision,
    actual_cost double precision,
    triggered_by integer,
    triggered_by_ai boolean,
    logs text,
    error_message text,
    created_at timestamp without time zone,
    started_at timestamp without time zone,
    completed_at timestamp without time zone
);


ALTER TABLE public.devops_automation_jobs OWNER TO postgres;

--
-- Name: devops_automation_jobs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.devops_automation_jobs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.devops_automation_jobs_id_seq OWNER TO postgres;

--
-- Name: devops_automation_jobs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.devops_automation_jobs_id_seq OWNED BY public.devops_automation_jobs.id;


--
-- Name: esg_scores; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.esg_scores (
    id integer NOT NULL,
    company_name character varying(255) NOT NULL,
    ticker character varying(20),
    environmental_score double precision,
    social_score double precision,
    governance_score double precision,
    overall_esg_score double precision NOT NULL,
    security_score double precision,
    security_weight double precision,
    vulnerabilities_impact json,
    data_breach_history json,
    cybersecurity_investment double precision,
    security_certifications json,
    report_url character varying(500),
    rating_date timestamp without time zone NOT NULL,
    created_at timestamp without time zone
);


ALTER TABLE public.esg_scores OWNER TO postgres;

--
-- Name: esg_scores_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.esg_scores_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.esg_scores_id_seq OWNER TO postgres;

--
-- Name: esg_scores_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.esg_scores_id_seq OWNED BY public.esg_scores.id;


--
-- Name: exploit_chains; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exploit_chains (
    id integer NOT NULL,
    name character varying(500) NOT NULL,
    description text,
    bug_ids json NOT NULL,
    combined_severity public.bugseverity NOT NULL,
    combined_cvss double precision,
    chain_logic text,
    execution_steps json,
    impact text,
    bounty_potential double precision,
    created_at timestamp without time zone
);


ALTER TABLE public.exploit_chains OWNER TO postgres;

--
-- Name: exploit_chains_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.exploit_chains_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.exploit_chains_id_seq OWNER TO postgres;

--
-- Name: exploit_chains_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.exploit_chains_id_seq OWNED BY public.exploit_chains.id;


--
-- Name: exploit_database; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exploit_database (
    id integer NOT NULL,
    exploit_name character varying(500) NOT NULL,
    exploit_type character varying(100) NOT NULL,
    target_tech character varying(255),
    target_version character varying(100),
    cve_id character varying(50),
    cvss_score double precision,
    exploit_code text,
    payload text,
    discovery_method text,
    exploitation_steps json,
    fix_pattern text,
    fix_code text,
    successful_exploits integer,
    false_positives integer,
    companies_affected json,
    is_public boolean,
    disclosure_date timestamp without time zone,
    license_required boolean,
    license_price double precision,
    intel_metadata json,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.exploit_database OWNER TO postgres;

--
-- Name: exploit_database_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.exploit_database_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.exploit_database_id_seq OWNER TO postgres;

--
-- Name: exploit_database_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.exploit_database_id_seq OWNED BY public.exploit_database.id;


--
-- Name: fix_offers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fix_offers (
    id integer NOT NULL,
    bug_id integer NOT NULL,
    developer_id integer NOT NULL,
    status public.fixstatus NOT NULL,
    estimated_hours double precision NOT NULL,
    hourly_rate double precision NOT NULL,
    total_cost double precision NOT NULL,
    description text,
    technical_approach text,
    timeline character varying(255),
    pull_request_url character varying(500),
    commit_hash character varying(255),
    accepted_at timestamp without time zone,
    started_at timestamp without time zone,
    completed_at timestamp without time zone,
    verified_at timestamp without time zone,
    rating integer,
    review text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.fix_offers OWNER TO postgres;

--
-- Name: fix_offers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fix_offers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.fix_offers_id_seq OWNER TO postgres;

--
-- Name: fix_offers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fix_offers_id_seq OWNED BY public.fix_offers.id;


--
-- Name: geopolitical_contracts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.geopolitical_contracts (
    id integer NOT NULL,
    contract_type character varying(100) NOT NULL,
    government_entity character varying(255) NOT NULL,
    country character varying(100) NOT NULL,
    contract_value double precision NOT NULL,
    currency character varying(10),
    scope text,
    deliverables json,
    classification_level character varying(50),
    start_date timestamp without time zone NOT NULL,
    end_date timestamp without time zone NOT NULL,
    status character varying(50),
    bugs_delivered integer,
    reports_delivered integer,
    payment_schedule json,
    payments_received json,
    is_confidential boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.geopolitical_contracts OWNER TO postgres;

--
-- Name: geopolitical_contracts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.geopolitical_contracts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.geopolitical_contracts_id_seq OWNER TO postgres;

--
-- Name: geopolitical_contracts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.geopolitical_contracts_id_seq OWNED BY public.geopolitical_contracts.id;


--
-- Name: guild_memberships; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.guild_memberships (
    id integer NOT NULL,
    user_id integer NOT NULL,
    tier public.guildmembershiptier NOT NULL,
    total_earnings double precision,
    annual_dues double precision NOT NULL,
    dues_paid boolean,
    voting_power integer,
    joined_at timestamp without time zone NOT NULL,
    last_payment_date timestamp without time zone,
    next_payment_date timestamp without time zone,
    benefits json,
    strikes integer,
    warnings integer,
    is_active boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.guild_memberships OWNER TO postgres;

--
-- Name: guild_memberships_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.guild_memberships_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.guild_memberships_id_seq OWNER TO postgres;

--
-- Name: guild_memberships_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.guild_memberships_id_seq OWNED BY public.guild_memberships.id;


--
-- Name: guild_proposals; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.guild_proposals (
    id integer NOT NULL,
    proposer_id integer NOT NULL,
    title character varying(500) NOT NULL,
    description text NOT NULL,
    proposal_type character varying(50) NOT NULL,
    target_platform character varying(100),
    target_company character varying(255),
    action_requested text,
    votes_for integer,
    votes_against integer,
    votes_abstain integer,
    voting_threshold double precision,
    status character varying(50),
    voting_starts timestamp without time zone NOT NULL,
    voting_ends timestamp without time zone NOT NULL,
    result character varying(50),
    executed boolean,
    executed_at timestamp without time zone,
    created_at timestamp without time zone
);


ALTER TABLE public.guild_proposals OWNER TO postgres;

--
-- Name: guild_proposals_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.guild_proposals_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.guild_proposals_id_seq OWNER TO postgres;

--
-- Name: guild_proposals_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.guild_proposals_id_seq OWNED BY public.guild_proposals.id;


--
-- Name: infrastructure_resources; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.infrastructure_resources (
    id integer NOT NULL,
    resource_type character varying(100) NOT NULL,
    resource_name character varying(255) NOT NULL,
    company_id integer NOT NULL,
    cloud_provider character varying(50),
    region character varying(100),
    resource_id character varying(255),
    configuration json,
    status character varying(50),
    monthly_cost double precision,
    provisioned_by_job_id integer,
    auto_scaling_enabled boolean,
    created_at timestamp without time zone,
    last_modified timestamp without time zone
);


ALTER TABLE public.infrastructure_resources OWNER TO postgres;

--
-- Name: infrastructure_resources_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.infrastructure_resources_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.infrastructure_resources_id_seq OWNER TO postgres;

--
-- Name: infrastructure_resources_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.infrastructure_resources_id_seq OWNED BY public.infrastructure_resources.id;


--
-- Name: insurance_claims; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.insurance_claims (
    id integer NOT NULL,
    policy_id integer NOT NULL,
    claim_number character varying(50) NOT NULL,
    bug_id integer,
    claim_amount double precision NOT NULL,
    approved_amount double precision,
    status public.insuranceclaimstatus,
    incident_description text NOT NULL,
    incident_date timestamp without time zone NOT NULL,
    supporting_documents json,
    reviewer_notes text,
    reviewed_by integer,
    reviewed_at timestamp without time zone,
    payment_date timestamp without time zone,
    payment_reference character varying(255),
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.insurance_claims OWNER TO postgres;

--
-- Name: insurance_claims_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.insurance_claims_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.insurance_claims_id_seq OWNER TO postgres;

--
-- Name: insurance_claims_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.insurance_claims_id_seq OWNED BY public.insurance_claims.id;


--
-- Name: insurance_policies; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.insurance_policies (
    id integer NOT NULL,
    company_id integer NOT NULL,
    policy_number character varying(50) NOT NULL,
    coverage_amount double precision NOT NULL,
    premium_amount double precision NOT NULL,
    policy_type character varying(100),
    start_date timestamp without time zone NOT NULL,
    end_date timestamp without time zone NOT NULL,
    status public.insurancepolicystatus,
    covered_assets json,
    pre_audit_score double precision,
    risk_level character varying(50),
    terms_conditions text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.insurance_policies OWNER TO postgres;

--
-- Name: insurance_policies_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.insurance_policies_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.insurance_policies_id_seq OWNER TO postgres;

--
-- Name: insurance_policies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.insurance_policies_id_seq OWNED BY public.insurance_policies.id;


--
-- Name: insurance_premium_payments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.insurance_premium_payments (
    id integer NOT NULL,
    policy_id integer NOT NULL,
    payment_amount double precision NOT NULL,
    payment_date timestamp without time zone NOT NULL,
    payment_method character varying(50),
    payment_reference character varying(255),
    billing_period_start timestamp without time zone,
    billing_period_end timestamp without time zone,
    status character varying(50),
    created_at timestamp without time zone
);


ALTER TABLE public.insurance_premium_payments OWNER TO postgres;

--
-- Name: insurance_premium_payments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.insurance_premium_payments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.insurance_premium_payments_id_seq OWNER TO postgres;

--
-- Name: insurance_premium_payments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.insurance_premium_payments_id_seq OWNED BY public.insurance_premium_payments.id;


--
-- Name: intelligence_reports; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.intelligence_reports (
    id integer NOT NULL,
    report_type character varying(100) NOT NULL,
    title character varying(500) NOT NULL,
    target_company character varying(255),
    target_industry character varying(100),
    executive_summary text,
    detailed_analysis text,
    recommendations text,
    security_score double precision,
    risk_level character varying(50),
    vulnerabilities_analyzed integer,
    data_sources json,
    charts json,
    tables json,
    buyer_id integer,
    price double precision,
    is_confidential boolean,
    generated_at timestamp without time zone NOT NULL,
    purchased_at timestamp without time zone,
    created_at timestamp without time zone
);


ALTER TABLE public.intelligence_reports OWNER TO postgres;

--
-- Name: intelligence_reports_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.intelligence_reports_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.intelligence_reports_id_seq OWNER TO postgres;

--
-- Name: intelligence_reports_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.intelligence_reports_id_seq OWNED BY public.intelligence_reports.id;


--
-- Name: marketplace_listings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.marketplace_listings (
    id integer NOT NULL,
    bug_id integer NOT NULL,
    seller_id integer NOT NULL,
    listing_type character varying(50) NOT NULL,
    asking_price double precision NOT NULL,
    currency character varying(10),
    is_private boolean,
    is_exclusive boolean,
    description text,
    terms text,
    views integer,
    interested_buyers json,
    status character varying(50),
    sold_at timestamp without time zone,
    buyer_id integer,
    sale_price double precision,
    platform_fee double precision,
    seller_payout double precision,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.marketplace_listings OWNER TO postgres;

--
-- Name: marketplace_listings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.marketplace_listings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.marketplace_listings_id_seq OWNER TO postgres;

--
-- Name: marketplace_listings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.marketplace_listings_id_seq OWNED BY public.marketplace_listings.id;


--
-- Name: payments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.payments (
    id integer NOT NULL,
    user_id integer NOT NULL,
    payment_type character varying(50) NOT NULL,
    status public.paymentstatus NOT NULL,
    amount double precision NOT NULL,
    currency character varying(10),
    stripe_payment_id character varying(255),
    stripe_charge_id character varying(255),
    crypto_tx_hash character varying(255),
    crypto_wallet character varying(255),
    description text,
    payment_metadata json,
    related_id integer,
    related_type character varying(50),
    processed_at timestamp without time zone,
    created_at timestamp without time zone
);


ALTER TABLE public.payments OWNER TO postgres;

--
-- Name: payments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.payments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.payments_id_seq OWNER TO postgres;

--
-- Name: payments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.payments_id_seq OWNED BY public.payments.id;


--
-- Name: posts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.posts (
    id integer NOT NULL,
    user_id integer NOT NULL,
    content text NOT NULL,
    post_type character varying(50),
    bug_id integer,
    media_urls json,
    likes_count integer,
    comments_count integer,
    shares_count integer,
    is_public boolean,
    hashtags json,
    mentions json,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.posts OWNER TO postgres;

--
-- Name: posts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.posts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.posts_id_seq OWNER TO postgres;

--
-- Name: posts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.posts_id_seq OWNED BY public.posts.id;


--
-- Name: quantum_jobs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quantum_jobs (
    id integer NOT NULL,
    user_id integer NOT NULL,
    job_type character varying(100) NOT NULL,
    target_url character varying(1000),
    target_tech character varying(255),
    quantum_algorithm character varying(100),
    quantum_provider character varying(50),
    circuit_depth integer,
    qubit_count integer,
    status character varying(50),
    start_time timestamp without time zone,
    end_time timestamp without time zone,
    execution_time_seconds integer,
    results json,
    vulnerabilities_found json,
    cost double precision,
    error_message text,
    created_at timestamp without time zone
);


ALTER TABLE public.quantum_jobs OWNER TO postgres;

--
-- Name: quantum_jobs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.quantum_jobs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.quantum_jobs_id_seq OWNER TO postgres;

--
-- Name: quantum_jobs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.quantum_jobs_id_seq OWNED BY public.quantum_jobs.id;


--
-- Name: sanction_targets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sanction_targets (
    id integer NOT NULL,
    target_company character varying(255) NOT NULL,
    target_domain character varying(255) NOT NULL,
    issue_type character varying(100) NOT NULL,
    issue_description text,
    evidence json,
    vulnerabilities_found json,
    leverage_points json,
    campaign_status character varying(50),
    partner_ngos json,
    media_coverage json,
    deadline timestamp without time zone,
    outcome character varying(50),
    outcome_description text,
    impact_metrics json,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.sanction_targets OWNER TO postgres;

--
-- Name: sanction_targets_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sanction_targets_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sanction_targets_id_seq OWNER TO postgres;

--
-- Name: sanction_targets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sanction_targets_id_seq OWNED BY public.sanction_targets.id;


--
-- Name: satellite_intelligence; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.satellite_intelligence (
    id integer NOT NULL,
    target_company character varying(255) NOT NULL,
    target_location character varying(255),
    latitude double precision,
    longitude double precision,
    facility_type character varying(100),
    facility_size double precision,
    imagery_date timestamp without time zone,
    imagery_provider character varying(100),
    imagery_url character varying(500),
    analysis text,
    infrastructure_detected json,
    network_expansions json,
    new_deployments json,
    risk_assessment text,
    recommendations text,
    correlation_with_cyber json,
    confidence_score double precision,
    created_at timestamp without time zone
);


ALTER TABLE public.satellite_intelligence OWNER TO postgres;

--
-- Name: satellite_intelligence_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.satellite_intelligence_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.satellite_intelligence_id_seq OWNER TO postgres;

--
-- Name: satellite_intelligence_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.satellite_intelligence_id_seq OWNED BY public.satellite_intelligence.id;


--
-- Name: scans; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.scans (
    id integer NOT NULL,
    user_id integer NOT NULL,
    target_url character varying(1000) NOT NULL,
    target_domain character varying(255) NOT NULL,
    scan_type character varying(50),
    status character varying(50),
    start_time timestamp without time zone,
    end_time timestamp without time zone,
    duration_seconds integer,
    agents_used integer,
    endpoints_tested integer,
    vulnerabilities_found integer,
    discovery_phase_time integer,
    validation_phase_time integer,
    reporting_phase_time integer,
    reconnaissance_data json,
    tech_stack json,
    success boolean,
    error_message text,
    scan_metadata json,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.scans OWNER TO postgres;

--
-- Name: scans_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.scans_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.scans_id_seq OWNER TO postgres;

--
-- Name: scans_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.scans_id_seq OWNED BY public.scans.id;


--
-- Name: security_credit_scores; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.security_credit_scores (
    id integer NOT NULL,
    company_id integer NOT NULL,
    score integer NOT NULL,
    grade character varying(10),
    technical_security_score double precision,
    process_maturity_score double precision,
    compliance_score double precision,
    historical_track_record_score double precision,
    vulnerability_count integer,
    critical_vulnerabilities integer,
    high_vulnerabilities integer,
    patch_velocity_days double precision,
    incident_count integer,
    breach_count integer,
    certifications json,
    calculated_at timestamp without time zone NOT NULL,
    valid_until timestamp without time zone,
    report_url character varying(1000),
    created_at timestamp without time zone
);


ALTER TABLE public.security_credit_scores OWNER TO postgres;

--
-- Name: security_credit_scores_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.security_credit_scores_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.security_credit_scores_id_seq OWNER TO postgres;

--
-- Name: security_credit_scores_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.security_credit_scores_id_seq OWNED BY public.security_credit_scores.id;


--
-- Name: security_score_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.security_score_history (
    id integer NOT NULL,
    company_id integer NOT NULL,
    score integer NOT NULL,
    change_from_previous integer,
    factors_improved json,
    factors_degraded json,
    recorded_at timestamp without time zone NOT NULL
);


ALTER TABLE public.security_score_history OWNER TO postgres;

--
-- Name: security_score_history_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.security_score_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.security_score_history_id_seq OWNER TO postgres;

--
-- Name: security_score_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.security_score_history_id_seq OWNED BY public.security_score_history.id;


--
-- Name: security_score_reports; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.security_score_reports (
    id integer NOT NULL,
    score_id integer NOT NULL,
    report_type character varying(50) NOT NULL,
    detailed_analysis text,
    recommendations json,
    executive_summary text,
    technical_details json,
    generated_by integer,
    generated_at timestamp without time zone,
    purchased_by integer,
    purchase_price double precision,
    purchased_at timestamp without time zone,
    access_token character varying(255)
);


ALTER TABLE public.security_score_reports OWNER TO postgres;

--
-- Name: security_score_reports_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.security_score_reports_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.security_score_reports_id_seq OWNER TO postgres;

--
-- Name: security_score_reports_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.security_score_reports_id_seq OWNED BY public.security_score_reports.id;


--
-- Name: security_score_subscriptions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.security_score_subscriptions (
    id integer NOT NULL,
    subscriber_id integer NOT NULL,
    company_id integer NOT NULL,
    subscription_type character varying(50) NOT NULL,
    monitoring_frequency character varying(50),
    alert_thresholds json,
    active integer,
    start_date timestamp without time zone NOT NULL,
    end_date timestamp without time zone,
    created_at timestamp without time zone
);


ALTER TABLE public.security_score_subscriptions OWNER TO postgres;

--
-- Name: security_score_subscriptions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.security_score_subscriptions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.security_score_subscriptions_id_seq OWNER TO postgres;

--
-- Name: security_score_subscriptions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.security_score_subscriptions_id_seq OWNED BY public.security_score_subscriptions.id;


--
-- Name: security_scores; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.security_scores (
    id integer NOT NULL,
    company_id integer,
    company_name character varying(255) NOT NULL,
    domain character varying(255) NOT NULL,
    overall_score double precision NOT NULL,
    vulnerability_score double precision,
    fix_response_score double precision,
    disclosure_score double precision,
    total_bugs_found integer,
    critical_bugs integer,
    high_bugs integer,
    medium_bugs integer,
    low_bugs integer,
    avg_fix_time_days double precision,
    bugs_fixed integer,
    bugs_unfixed integer,
    last_bug_date timestamp without time zone,
    last_fix_date timestamp without time zone,
    tech_stack json,
    vulnerability_trends json,
    industry character varying(100),
    company_size character varying(50),
    historical_scores json,
    report_generated boolean,
    report_url character varying(500),
    report_price double precision,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.security_scores OWNER TO postgres;

--
-- Name: security_scores_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.security_scores_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.security_scores_id_seq OWNER TO postgres;

--
-- Name: security_scores_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.security_scores_id_seq OWNED BY public.security_scores.id;


--
-- Name: self_healing_events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.self_healing_events (
    id integer NOT NULL,
    incident_type character varying(100) NOT NULL,
    resource_id integer,
    detected_at timestamp without time zone NOT NULL,
    severity character varying(50),
    symptoms json,
    root_cause_analysis text,
    healing_action_taken text NOT NULL,
    healing_status character varying(50),
    resolved_at timestamp without time zone,
    resolution_time_seconds integer,
    ai_confidence_score double precision,
    manual_intervention_required boolean,
    created_at timestamp without time zone
);


ALTER TABLE public.self_healing_events OWNER TO postgres;

--
-- Name: self_healing_events_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.self_healing_events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.self_healing_events_id_seq OWNER TO postgres;

--
-- Name: self_healing_events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.self_healing_events_id_seq OWNED BY public.self_healing_events.id;


--
-- Name: social_connections; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.social_connections (
    id integer NOT NULL,
    user_id integer NOT NULL,
    connected_user_id integer NOT NULL,
    connection_type character varying(50),
    is_mutual boolean,
    created_at timestamp without time zone
);


ALTER TABLE public.social_connections OWNER TO postgres;

--
-- Name: social_connections_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.social_connections_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.social_connections_id_seq OWNER TO postgres;

--
-- Name: social_connections_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.social_connections_id_seq OWNED BY public.social_connections.id;


--
-- Name: students; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.students (
    id integer NOT NULL,
    user_id integer NOT NULL,
    university_id integer NOT NULL,
    student_id_number character varying(100) NOT NULL,
    enrollment_date timestamp without time zone NOT NULL,
    expected_graduation timestamp without time zone,
    graduation_date timestamp without time zone,
    year integer,
    semester integer,
    gpa double precision,
    bugs_found integer,
    bugs_required integer,
    courses_completed json,
    current_courses json,
    certification_level character varying(50),
    certifications json,
    portfolio_url character varying(500),
    job_placement boolean,
    employer character varying(255),
    starting_salary double precision,
    is_active boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.students OWNER TO postgres;

--
-- Name: students_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.students_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.students_id_seq OWNER TO postgres;

--
-- Name: students_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.students_id_seq OWNED BY public.students.id;


--
-- Name: subscription_boxes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.subscription_boxes (
    id integer NOT NULL,
    company_id integer NOT NULL,
    tier character varying(50) NOT NULL,
    monthly_fee double precision NOT NULL,
    bug_quota integer NOT NULL,
    bugs_found integer,
    guaranteed_severity public.bugseverity,
    domains json,
    scope json,
    status character varying(50),
    start_date timestamp without time zone NOT NULL,
    end_date timestamp without time zone,
    created_at timestamp without time zone
);


ALTER TABLE public.subscription_boxes OWNER TO postgres;

--
-- Name: subscription_boxes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.subscription_boxes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.subscription_boxes_id_seq OWNER TO postgres;

--
-- Name: subscription_boxes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.subscription_boxes_id_seq OWNED BY public.subscription_boxes.id;


--
-- Name: subscriptions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.subscriptions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    tier public.subscriptiontier NOT NULL,
    status character varying(50),
    stripe_subscription_id character varying(255),
    stripe_customer_id character varying(255),
    price double precision NOT NULL,
    billing_cycle character varying(50),
    features text,
    scans_limit integer,
    scans_used integer,
    start_date timestamp without time zone NOT NULL,
    end_date timestamp without time zone,
    next_billing_date timestamp without time zone,
    auto_renew boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.subscriptions OWNER TO postgres;

--
-- Name: subscriptions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.subscriptions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.subscriptions_id_seq OWNER TO postgres;

--
-- Name: subscriptions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.subscriptions_id_seq OWNED BY public.subscriptions.id;


--
-- Name: university_partnerships; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.university_partnerships (
    id integer NOT NULL,
    university_name character varying(255) NOT NULL,
    university_code character varying(50) NOT NULL,
    country character varying(100),
    city character varying(100),
    contact_name character varying(255),
    contact_email character varying(255),
    contact_phone character varying(50),
    program_start_date timestamp without time zone,
    program_status character varying(50),
    annual_license_fee double precision NOT NULL,
    student_platform_fee double precision,
    enrolled_students integer,
    graduated_students integer,
    curriculum_version character varying(50),
    features_enabled json,
    total_bugs_found integer,
    total_bounties_earned double precision,
    placement_rate double precision,
    avg_starting_salary double precision,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.university_partnerships OWNER TO postgres;

--
-- Name: university_partnerships_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.university_partnerships_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.university_partnerships_id_seq OWNER TO postgres;

--
-- Name: university_partnerships_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.university_partnerships_id_seq OWNED BY public.university_partnerships.id;


--
-- Name: user_profiles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_profiles (
    id integer NOT NULL,
    user_id integer NOT NULL,
    about_me text,
    experience_years integer,
    total_scans integer,
    successful_reports integer,
    acceptance_rate double precision,
    avg_severity double precision,
    fastest_discovery integer,
    longest_chain integer,
    preferred_platforms text,
    preferred_vulnerabilities text,
    preferred_industries text,
    certification_level character varying(50),
    certifications text,
    education text,
    ai_clone_enabled boolean,
    ai_clone_earnings double precision,
    portfolio_url character varying(500),
    blog_url character varying(500),
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.user_profiles OWNER TO postgres;

--
-- Name: user_profiles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_profiles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_profiles_id_seq OWNER TO postgres;

--
-- Name: user_profiles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_profiles_id_seq OWNED BY public.user_profiles.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    username character varying(100) NOT NULL,
    hashed_password character varying(255) NOT NULL,
    full_name character varying(255),
    role public.userrole NOT NULL,
    subscription_tier public.subscriptiontier NOT NULL,
    is_active boolean,
    is_verified boolean,
    is_premium boolean,
    api_key character varying(255),
    bio text,
    avatar_url character varying(500),
    location character varying(255),
    website character varying(500),
    github_username character varying(100),
    twitter_username character varying(100),
    linkedin_url character varying(500),
    discord_username character varying(100),
    total_bounties_earned double precision,
    total_bugs_found integer,
    reputation_score integer,
    hunter_rank integer,
    specializations text,
    skills text,
    email_notifications boolean,
    push_notifications boolean,
    last_login timestamp without time zone,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: vulnerability_forecasts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vulnerability_forecasts (
    id integer NOT NULL,
    forecast_period character varying(50) NOT NULL,
    industry character varying(100),
    tech_stack character varying(100),
    predicted_vulnerability_count integer,
    confidence_level double precision,
    vulnerability_type_distribution json,
    severity_distribution json,
    trending_vulnerabilities json,
    emerging_patterns json,
    market_intelligence json,
    recommendations text,
    data_points_analyzed integer,
    model_accuracy double precision,
    subscribers json,
    created_at timestamp without time zone
);


ALTER TABLE public.vulnerability_forecasts OWNER TO postgres;

--
-- Name: vulnerability_forecasts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.vulnerability_forecasts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.vulnerability_forecasts_id_seq OWNER TO postgres;

--
-- Name: vulnerability_forecasts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.vulnerability_forecasts_id_seq OWNED BY public.vulnerability_forecasts.id;


--
-- Name: vulnerability_patterns; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vulnerability_patterns (
    id integer NOT NULL,
    pattern_name character varying(255) NOT NULL,
    pattern_type public.bugtype NOT NULL,
    tech_stack json,
    framework character varying(100),
    version_range character varying(100),
    pattern_signature text,
    detection_rules json,
    success_rate double precision,
    false_positive_rate double precision,
    fixes_applied integer,
    fix_pattern text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.vulnerability_patterns OWNER TO postgres;

--
-- Name: vulnerability_patterns_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.vulnerability_patterns_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.vulnerability_patterns_id_seq OWNER TO postgres;

--
-- Name: vulnerability_patterns_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.vulnerability_patterns_id_seq OWNED BY public.vulnerability_patterns.id;


--
-- Name: agi_research_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agi_research_logs ALTER COLUMN id SET DEFAULT nextval('public.agi_research_logs_id_seq'::regclass);


--
-- Name: bci_security_audits id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bci_security_audits ALTER COLUMN id SET DEFAULT nextval('public.bci_security_audits_id_seq'::regclass);


--
-- Name: bug_derivatives id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_derivatives ALTER COLUMN id SET DEFAULT nextval('public.bug_derivatives_id_seq'::regclass);


--
-- Name: bug_future_positions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_future_positions ALTER COLUMN id SET DEFAULT nextval('public.bug_future_positions_id_seq'::regclass);


--
-- Name: bug_futures_extended id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_futures_extended ALTER COLUMN id SET DEFAULT nextval('public.bug_futures_extended_id_seq'::regclass);


--
-- Name: bug_futures_old id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_futures_old ALTER COLUMN id SET DEFAULT nextval('public.bug_futures_old_id_seq'::regclass);


--
-- Name: bug_index_funds id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_index_funds ALTER COLUMN id SET DEFAULT nextval('public.bug_index_funds_id_seq'::regclass);


--
-- Name: bug_marketplace_listings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_marketplace_listings ALTER COLUMN id SET DEFAULT nextval('public.bug_marketplace_listings_id_seq'::regclass);


--
-- Name: bug_marketplace_trades id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_marketplace_trades ALTER COLUMN id SET DEFAULT nextval('public.bug_marketplace_trades_id_seq'::regclass);


--
-- Name: bug_nfts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_nfts ALTER COLUMN id SET DEFAULT nextval('public.bug_nfts_id_seq'::regclass);


--
-- Name: bugs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bugs ALTER COLUMN id SET DEFAULT nextval('public.bugs_id_seq'::regclass);


--
-- Name: comments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comments ALTER COLUMN id SET DEFAULT nextval('public.comments_id_seq'::regclass);


--
-- Name: cost_optimization_recommendations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_optimization_recommendations ALTER COLUMN id SET DEFAULT nextval('public.cost_optimization_recommendations_id_seq'::regclass);


--
-- Name: courses id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.courses ALTER COLUMN id SET DEFAULT nextval('public.courses_id_seq'::regclass);


--
-- Name: creator_subscriptions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.creator_subscriptions ALTER COLUMN id SET DEFAULT nextval('public.creator_subscriptions_id_seq'::regclass);


--
-- Name: dao_governance_extended id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dao_governance_extended ALTER COLUMN id SET DEFAULT nextval('public.dao_governance_extended_id_seq'::regclass);


--
-- Name: dao_governance_old id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dao_governance_old ALTER COLUMN id SET DEFAULT nextval('public.dao_governance_old_id_seq'::regclass);


--
-- Name: dao_proposals id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dao_proposals ALTER COLUMN id SET DEFAULT nextval('public.dao_proposals_id_seq'::regclass);


--
-- Name: dao_tokens id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dao_tokens ALTER COLUMN id SET DEFAULT nextval('public.dao_tokens_id_seq'::regclass);


--
-- Name: dao_treasury_transactions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dao_treasury_transactions ALTER COLUMN id SET DEFAULT nextval('public.dao_treasury_transactions_id_seq'::regclass);


--
-- Name: dao_votes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dao_votes ALTER COLUMN id SET DEFAULT nextval('public.dao_votes_id_seq'::regclass);


--
-- Name: deployment_executions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deployment_executions ALTER COLUMN id SET DEFAULT nextval('public.deployment_executions_id_seq'::regclass);


--
-- Name: deployment_pipelines id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deployment_pipelines ALTER COLUMN id SET DEFAULT nextval('public.deployment_pipelines_id_seq'::regclass);


--
-- Name: devops_automation_jobs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.devops_automation_jobs ALTER COLUMN id SET DEFAULT nextval('public.devops_automation_jobs_id_seq'::regclass);


--
-- Name: esg_scores id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.esg_scores ALTER COLUMN id SET DEFAULT nextval('public.esg_scores_id_seq'::regclass);


--
-- Name: exploit_chains id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exploit_chains ALTER COLUMN id SET DEFAULT nextval('public.exploit_chains_id_seq'::regclass);


--
-- Name: exploit_database id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exploit_database ALTER COLUMN id SET DEFAULT nextval('public.exploit_database_id_seq'::regclass);


--
-- Name: fix_offers id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fix_offers ALTER COLUMN id SET DEFAULT nextval('public.fix_offers_id_seq'::regclass);


--
-- Name: geopolitical_contracts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.geopolitical_contracts ALTER COLUMN id SET DEFAULT nextval('public.geopolitical_contracts_id_seq'::regclass);


--
-- Name: guild_memberships id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.guild_memberships ALTER COLUMN id SET DEFAULT nextval('public.guild_memberships_id_seq'::regclass);


--
-- Name: guild_proposals id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.guild_proposals ALTER COLUMN id SET DEFAULT nextval('public.guild_proposals_id_seq'::regclass);


--
-- Name: infrastructure_resources id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.infrastructure_resources ALTER COLUMN id SET DEFAULT nextval('public.infrastructure_resources_id_seq'::regclass);


--
-- Name: insurance_claims id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.insurance_claims ALTER COLUMN id SET DEFAULT nextval('public.insurance_claims_id_seq'::regclass);


--
-- Name: insurance_policies id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.insurance_policies ALTER COLUMN id SET DEFAULT nextval('public.insurance_policies_id_seq'::regclass);


--
-- Name: insurance_premium_payments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.insurance_premium_payments ALTER COLUMN id SET DEFAULT nextval('public.insurance_premium_payments_id_seq'::regclass);


--
-- Name: intelligence_reports id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.intelligence_reports ALTER COLUMN id SET DEFAULT nextval('public.intelligence_reports_id_seq'::regclass);


--
-- Name: marketplace_listings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.marketplace_listings ALTER COLUMN id SET DEFAULT nextval('public.marketplace_listings_id_seq'::regclass);


--
-- Name: payments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments ALTER COLUMN id SET DEFAULT nextval('public.payments_id_seq'::regclass);


--
-- Name: posts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.posts ALTER COLUMN id SET DEFAULT nextval('public.posts_id_seq'::regclass);


--
-- Name: quantum_jobs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quantum_jobs ALTER COLUMN id SET DEFAULT nextval('public.quantum_jobs_id_seq'::regclass);


--
-- Name: sanction_targets id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sanction_targets ALTER COLUMN id SET DEFAULT nextval('public.sanction_targets_id_seq'::regclass);


--
-- Name: satellite_intelligence id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.satellite_intelligence ALTER COLUMN id SET DEFAULT nextval('public.satellite_intelligence_id_seq'::regclass);


--
-- Name: scans id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scans ALTER COLUMN id SET DEFAULT nextval('public.scans_id_seq'::regclass);


--
-- Name: security_credit_scores id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.security_credit_scores ALTER COLUMN id SET DEFAULT nextval('public.security_credit_scores_id_seq'::regclass);


--
-- Name: security_score_history id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.security_score_history ALTER COLUMN id SET DEFAULT nextval('public.security_score_history_id_seq'::regclass);


--
-- Name: security_score_reports id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.security_score_reports ALTER COLUMN id SET DEFAULT nextval('public.security_score_reports_id_seq'::regclass);


--
-- Name: security_score_subscriptions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.security_score_subscriptions ALTER COLUMN id SET DEFAULT nextval('public.security_score_subscriptions_id_seq'::regclass);


--
-- Name: security_scores id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.security_scores ALTER COLUMN id SET DEFAULT nextval('public.security_scores_id_seq'::regclass);


--
-- Name: self_healing_events id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.self_healing_events ALTER COLUMN id SET DEFAULT nextval('public.self_healing_events_id_seq'::regclass);


--
-- Name: social_connections id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.social_connections ALTER COLUMN id SET DEFAULT nextval('public.social_connections_id_seq'::regclass);


--
-- Name: students id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students ALTER COLUMN id SET DEFAULT nextval('public.students_id_seq'::regclass);


--
-- Name: subscription_boxes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscription_boxes ALTER COLUMN id SET DEFAULT nextval('public.subscription_boxes_id_seq'::regclass);


--
-- Name: subscriptions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscriptions ALTER COLUMN id SET DEFAULT nextval('public.subscriptions_id_seq'::regclass);


--
-- Name: university_partnerships id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.university_partnerships ALTER COLUMN id SET DEFAULT nextval('public.university_partnerships_id_seq'::regclass);


--
-- Name: user_profiles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_profiles ALTER COLUMN id SET DEFAULT nextval('public.user_profiles_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: vulnerability_forecasts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vulnerability_forecasts ALTER COLUMN id SET DEFAULT nextval('public.vulnerability_forecasts_id_seq'::regclass);


--
-- Name: vulnerability_patterns id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vulnerability_patterns ALTER COLUMN id SET DEFAULT nextval('public.vulnerability_patterns_id_seq'::regclass);


--
-- Data for Name: agi_research_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.agi_research_logs (id, experiment_name, experiment_type, model_architecture, model_parameters, training_data_size, training_duration, performance_metrics, bugs_discovered, novel_vulnerabilities, success_rate, false_positive_rate, insights, limitations, next_steps, budget_used, created_at) FROM stdin;
\.


--
-- Data for Name: bci_security_audits; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bci_security_audits (id, device_manufacturer, device_model, firmware_version, audit_type, vulnerabilities_found, neural_data_privacy_score, device_security_score, authentication_score, recommendations, audit_date, auditor_id, report_url, is_confidential, created_at) FROM stdin;
\.


--
-- Data for Name: bug_derivatives; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bug_derivatives (id, derivative_type, underlying_asset, prediction, confidence_percentage, strike_condition, expiry_date, premium, payout, seller_id, buyer_id, status, outcome, settled_at, created_at) FROM stdin;
\.


--
-- Data for Name: bug_future_positions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bug_future_positions (id, future_id, user_id, position_type, quantity, entry_price, current_value, unrealized_pnl, status, opened_at, closed_at, realized_pnl) FROM stdin;
\.


--
-- Data for Name: bug_futures_extended; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bug_futures_extended (id, contract_name, target_company, target_technology, vulnerability_type, contract_price, payout_condition, expiration_date, status, creator_id, total_contracts_issued, total_contracts_traded, created_at) FROM stdin;
\.


--
-- Data for Name: bug_futures_old; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bug_futures_old (id, buyer_id, target_company, target_domain, requested_severity, requested_types, budget, deadline, requirements, special_instructions, status, assigned_hunter_id, assigned_at, completed_at, bug_id, created_at) FROM stdin;
\.


--
-- Data for Name: bug_index_funds; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bug_index_funds (id, fund_name, fund_symbol, description, strategy, total_value, shares_outstanding, nav_per_share, bug_portfolio, industry_allocation, severity_allocation, ytd_return, inception_return, management_fee, performance_fee, minimum_investment, investors, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: bug_marketplace_listings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bug_marketplace_listings (id, bug_id, seller_id, listing_price, instant_payment_percentage, original_bounty_amount, status, verification_status, verified_at, listing_type, description, listed_at, sold_at, views_count, created_at) FROM stdin;
\.


--
-- Data for Name: bug_marketplace_trades; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bug_marketplace_trades (id, listing_id, buyer_id, seller_id, trade_price, platform_fee, seller_receives, trade_status, payment_method, payment_reference, escrow_released, escrow_released_at, traded_at, completed_at, created_at) FROM stdin;
\.


--
-- Data for Name: bug_nfts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bug_nfts (id, bug_id, owner_id, token_id, contract_address, blockchain, metadata_uri, nft_metadata, mint_price, current_price, royalty_percentage, is_listed, listing_price, transaction_history, minted_at, created_at) FROM stdin;
\.


--
-- Data for Name: bugs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bugs (id, hunter_id, scan_id, title, description, bug_type, severity, status, cvss_score, cwe_id, target_url, target_domain, endpoint, parameter, steps_to_reproduce, proof_of_concept, impact, remediation, exploit_code, payload, screenshots, video_url, attachments, platform_name, platform_program_id, platform_report_id, is_chain, chain_bugs, chain_description, discovery_time_seconds, ai_generated, ai_confidence, bounty_amount, bounty_currency, private_sale, private_sale_amount, reported_at, accepted_at, fixed_at, paid_at, is_public, disclosure_date, tags, bug_metadata, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: comments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.comments (id, post_id, user_id, content, parent_comment_id, likes_count, created_at) FROM stdin;
\.


--
-- Data for Name: cost_optimization_recommendations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cost_optimization_recommendations (id, company_id, resource_id, recommendation_type, current_cost_monthly, projected_cost_monthly, savings_monthly, savings_percentage, recommendation_details, action_required, priority, status, implemented_at, actual_savings_monthly, created_at) FROM stdin;
\.


--
-- Data for Name: courses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.courses (id, instructor_id, title, description, category, difficulty, price, curriculum, enrolled_count, completed_count, rating, reviews_count, video_urls, resources, is_published, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: creator_subscriptions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.creator_subscriptions (id, creator_id, subscriber_id, tier, monthly_price, benefits, status, started_at, next_billing_date, created_at) FROM stdin;
\.


--
-- Data for Name: dao_governance_extended; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dao_governance_extended (id, dao_name, total_token_supply, circulating_supply, governance_token_symbol, treasury_balance, min_proposal_tokens, voting_period_hours, quorum_percentage, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: dao_governance_old; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dao_governance_old (id, token_symbol, token_name, total_supply, circulating_supply, token_price, market_cap, treasury_balance, treasury_assets, bug_portfolio_value, total_holders, governance_proposals, revenue_30d, revenue_ytd, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: dao_proposals; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dao_proposals (id, proposal_number, title, description, proposer_id, proposal_type, status, voting_starts_at, voting_ends_at, votes_for, votes_against, votes_abstain, total_voting_power, quorum_reached, execution_data, executed_at, executed_by, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: dao_tokens; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dao_tokens (id, user_id, token_balance, staked_balance, earned_from_bug_bounties, earned_from_marketplace, earned_from_governance, voting_power, last_updated, created_at) FROM stdin;
\.


--
-- Data for Name: dao_treasury_transactions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dao_treasury_transactions (id, transaction_type, amount, from_address, to_address, purpose, proposal_id, transaction_hash, executed_at) FROM stdin;
\.


--
-- Data for Name: dao_votes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dao_votes (id, proposal_id, voter_id, vote_choice, voting_power, reason, voted_at) FROM stdin;
\.


--
-- Data for Name: deployment_executions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.deployment_executions (id, pipeline_id, deployment_number, commit_hash, commit_message, triggered_by, triggered_by_ai, environment, status, stages_completed, started_at, completed_at, duration_seconds, logs_url, rollback_executed, created_at) FROM stdin;
\.


--
-- Data for Name: deployment_pipelines; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.deployment_pipelines (id, pipeline_name, company_id, repository_url, branch, pipeline_config, stages, auto_deploy, last_deployment_id, last_deployment_status, success_rate, average_duration_minutes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: devops_automation_jobs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.devops_automation_jobs (id, job_type, company_id, status, configuration, target_environment, target_region, estimated_duration_minutes, actual_duration_minutes, resources_created, cost_estimate, actual_cost, triggered_by, triggered_by_ai, logs, error_message, created_at, started_at, completed_at) FROM stdin;
\.


--
-- Data for Name: esg_scores; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.esg_scores (id, company_name, ticker, environmental_score, social_score, governance_score, overall_esg_score, security_score, security_weight, vulnerabilities_impact, data_breach_history, cybersecurity_investment, security_certifications, report_url, rating_date, created_at) FROM stdin;
\.


--
-- Data for Name: exploit_chains; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exploit_chains (id, name, description, bug_ids, combined_severity, combined_cvss, chain_logic, execution_steps, impact, bounty_potential, created_at) FROM stdin;
\.


--
-- Data for Name: exploit_database; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exploit_database (id, exploit_name, exploit_type, target_tech, target_version, cve_id, cvss_score, exploit_code, payload, discovery_method, exploitation_steps, fix_pattern, fix_code, successful_exploits, false_positives, companies_affected, is_public, disclosure_date, license_required, license_price, intel_metadata, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: fix_offers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fix_offers (id, bug_id, developer_id, status, estimated_hours, hourly_rate, total_cost, description, technical_approach, timeline, pull_request_url, commit_hash, accepted_at, started_at, completed_at, verified_at, rating, review, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: geopolitical_contracts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.geopolitical_contracts (id, contract_type, government_entity, country, contract_value, currency, scope, deliverables, classification_level, start_date, end_date, status, bugs_delivered, reports_delivered, payment_schedule, payments_received, is_confidential, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: guild_memberships; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.guild_memberships (id, user_id, tier, total_earnings, annual_dues, dues_paid, voting_power, joined_at, last_payment_date, next_payment_date, benefits, strikes, warnings, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: guild_proposals; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.guild_proposals (id, proposer_id, title, description, proposal_type, target_platform, target_company, action_requested, votes_for, votes_against, votes_abstain, voting_threshold, status, voting_starts, voting_ends, result, executed, executed_at, created_at) FROM stdin;
\.


--
-- Data for Name: infrastructure_resources; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.infrastructure_resources (id, resource_type, resource_name, company_id, cloud_provider, region, resource_id, configuration, status, monthly_cost, provisioned_by_job_id, auto_scaling_enabled, created_at, last_modified) FROM stdin;
\.


--
-- Data for Name: insurance_claims; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.insurance_claims (id, policy_id, claim_number, bug_id, claim_amount, approved_amount, status, incident_description, incident_date, supporting_documents, reviewer_notes, reviewed_by, reviewed_at, payment_date, payment_reference, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: insurance_policies; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.insurance_policies (id, company_id, policy_number, coverage_amount, premium_amount, policy_type, start_date, end_date, status, covered_assets, pre_audit_score, risk_level, terms_conditions, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: insurance_premium_payments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.insurance_premium_payments (id, policy_id, payment_amount, payment_date, payment_method, payment_reference, billing_period_start, billing_period_end, status, created_at) FROM stdin;
\.


--
-- Data for Name: intelligence_reports; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.intelligence_reports (id, report_type, title, target_company, target_industry, executive_summary, detailed_analysis, recommendations, security_score, risk_level, vulnerabilities_analyzed, data_sources, charts, tables, buyer_id, price, is_confidential, generated_at, purchased_at, created_at) FROM stdin;
\.


--
-- Data for Name: marketplace_listings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.marketplace_listings (id, bug_id, seller_id, listing_type, asking_price, currency, is_private, is_exclusive, description, terms, views, interested_buyers, status, sold_at, buyer_id, sale_price, platform_fee, seller_payout, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: payments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payments (id, user_id, payment_type, status, amount, currency, stripe_payment_id, stripe_charge_id, crypto_tx_hash, crypto_wallet, description, payment_metadata, related_id, related_type, processed_at, created_at) FROM stdin;
\.


--
-- Data for Name: posts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.posts (id, user_id, content, post_type, bug_id, media_urls, likes_count, comments_count, shares_count, is_public, hashtags, mentions, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: quantum_jobs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quantum_jobs (id, user_id, job_type, target_url, target_tech, quantum_algorithm, quantum_provider, circuit_depth, qubit_count, status, start_time, end_time, execution_time_seconds, results, vulnerabilities_found, cost, error_message, created_at) FROM stdin;
\.


--
-- Data for Name: sanction_targets; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sanction_targets (id, target_company, target_domain, issue_type, issue_description, evidence, vulnerabilities_found, leverage_points, campaign_status, partner_ngos, media_coverage, deadline, outcome, outcome_description, impact_metrics, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: satellite_intelligence; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.satellite_intelligence (id, target_company, target_location, latitude, longitude, facility_type, facility_size, imagery_date, imagery_provider, imagery_url, analysis, infrastructure_detected, network_expansions, new_deployments, risk_assessment, recommendations, correlation_with_cyber, confidence_score, created_at) FROM stdin;
\.


--
-- Data for Name: scans; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.scans (id, user_id, target_url, target_domain, scan_type, status, start_time, end_time, duration_seconds, agents_used, endpoints_tested, vulnerabilities_found, discovery_phase_time, validation_phase_time, reporting_phase_time, reconnaissance_data, tech_stack, success, error_message, scan_metadata, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: security_credit_scores; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.security_credit_scores (id, company_id, score, grade, technical_security_score, process_maturity_score, compliance_score, historical_track_record_score, vulnerability_count, critical_vulnerabilities, high_vulnerabilities, patch_velocity_days, incident_count, breach_count, certifications, calculated_at, valid_until, report_url, created_at) FROM stdin;
\.


--
-- Data for Name: security_score_history; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.security_score_history (id, company_id, score, change_from_previous, factors_improved, factors_degraded, recorded_at) FROM stdin;
\.


--
-- Data for Name: security_score_reports; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.security_score_reports (id, score_id, report_type, detailed_analysis, recommendations, executive_summary, technical_details, generated_by, generated_at, purchased_by, purchase_price, purchased_at, access_token) FROM stdin;
\.


--
-- Data for Name: security_score_subscriptions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.security_score_subscriptions (id, subscriber_id, company_id, subscription_type, monitoring_frequency, alert_thresholds, active, start_date, end_date, created_at) FROM stdin;
\.


--
-- Data for Name: security_scores; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.security_scores (id, company_id, company_name, domain, overall_score, vulnerability_score, fix_response_score, disclosure_score, total_bugs_found, critical_bugs, high_bugs, medium_bugs, low_bugs, avg_fix_time_days, bugs_fixed, bugs_unfixed, last_bug_date, last_fix_date, tech_stack, vulnerability_trends, industry, company_size, historical_scores, report_generated, report_url, report_price, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: self_healing_events; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.self_healing_events (id, incident_type, resource_id, detected_at, severity, symptoms, root_cause_analysis, healing_action_taken, healing_status, resolved_at, resolution_time_seconds, ai_confidence_score, manual_intervention_required, created_at) FROM stdin;
\.


--
-- Data for Name: social_connections; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.social_connections (id, user_id, connected_user_id, connection_type, is_mutual, created_at) FROM stdin;
\.


--
-- Data for Name: students; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.students (id, user_id, university_id, student_id_number, enrollment_date, expected_graduation, graduation_date, year, semester, gpa, bugs_found, bugs_required, courses_completed, current_courses, certification_level, certifications, portfolio_url, job_placement, employer, starting_salary, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: subscription_boxes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.subscription_boxes (id, company_id, tier, monthly_fee, bug_quota, bugs_found, guaranteed_severity, domains, scope, status, start_date, end_date, created_at) FROM stdin;
\.


--
-- Data for Name: subscriptions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.subscriptions (id, user_id, tier, status, stripe_subscription_id, stripe_customer_id, price, billing_cycle, features, scans_limit, scans_used, start_date, end_date, next_billing_date, auto_renew, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: university_partnerships; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.university_partnerships (id, university_name, university_code, country, city, contact_name, contact_email, contact_phone, program_start_date, program_status, annual_license_fee, student_platform_fee, enrolled_students, graduated_students, curriculum_version, features_enabled, total_bugs_found, total_bounties_earned, placement_rate, avg_starting_salary, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: user_profiles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_profiles (id, user_id, about_me, experience_years, total_scans, successful_reports, acceptance_rate, avg_severity, fastest_discovery, longest_chain, preferred_platforms, preferred_vulnerabilities, preferred_industries, certification_level, certifications, education, ai_clone_enabled, ai_clone_earnings, portfolio_url, blog_url, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, email, username, hashed_password, full_name, role, subscription_tier, is_active, is_verified, is_premium, api_key, bio, avatar_url, location, website, github_username, twitter_username, linkedin_url, discord_username, total_bounties_earned, total_bugs_found, reputation_score, hunter_rank, specializations, skills, email_notifications, push_notifications, last_login, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: vulnerability_forecasts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.vulnerability_forecasts (id, forecast_period, industry, tech_stack, predicted_vulnerability_count, confidence_level, vulnerability_type_distribution, severity_distribution, trending_vulnerabilities, emerging_patterns, market_intelligence, recommendations, data_points_analyzed, model_accuracy, subscribers, created_at) FROM stdin;
\.


--
-- Data for Name: vulnerability_patterns; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.vulnerability_patterns (id, pattern_name, pattern_type, tech_stack, framework, version_range, pattern_signature, detection_rules, success_rate, false_positive_rate, fixes_applied, fix_pattern, created_at, updated_at) FROM stdin;
\.


--
-- Name: agi_research_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.agi_research_logs_id_seq', 1, false);


--
-- Name: bci_security_audits_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bci_security_audits_id_seq', 1, false);


--
-- Name: bug_derivatives_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bug_derivatives_id_seq', 1, false);


--
-- Name: bug_future_positions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bug_future_positions_id_seq', 1, false);


--
-- Name: bug_futures_extended_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bug_futures_extended_id_seq', 1, false);


--
-- Name: bug_futures_old_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bug_futures_old_id_seq', 1, false);


--
-- Name: bug_index_funds_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bug_index_funds_id_seq', 1, false);


--
-- Name: bug_marketplace_listings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bug_marketplace_listings_id_seq', 1, false);


--
-- Name: bug_marketplace_trades_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bug_marketplace_trades_id_seq', 1, false);


--
-- Name: bug_nfts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bug_nfts_id_seq', 1, false);


--
-- Name: bugs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bugs_id_seq', 1, false);


--
-- Name: comments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.comments_id_seq', 1, false);


--
-- Name: cost_optimization_recommendations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.cost_optimization_recommendations_id_seq', 1, false);


--
-- Name: courses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.courses_id_seq', 1, false);


--
-- Name: creator_subscriptions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.creator_subscriptions_id_seq', 1, false);


--
-- Name: dao_governance_extended_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dao_governance_extended_id_seq', 1, false);


--
-- Name: dao_governance_old_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dao_governance_old_id_seq', 1, false);


--
-- Name: dao_proposals_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dao_proposals_id_seq', 1, false);


--
-- Name: dao_tokens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dao_tokens_id_seq', 1, false);


--
-- Name: dao_treasury_transactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dao_treasury_transactions_id_seq', 1, false);


--
-- Name: dao_votes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dao_votes_id_seq', 1, false);


--
-- Name: deployment_executions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.deployment_executions_id_seq', 1, false);


--
-- Name: deployment_pipelines_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.deployment_pipelines_id_seq', 1, false);


--
-- Name: devops_automation_jobs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.devops_automation_jobs_id_seq', 1, false);


--
-- Name: esg_scores_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.esg_scores_id_seq', 1, false);


--
-- Name: exploit_chains_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exploit_chains_id_seq', 1, false);


--
-- Name: exploit_database_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exploit_database_id_seq', 1, false);


--
-- Name: fix_offers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fix_offers_id_seq', 1, false);


--
-- Name: geopolitical_contracts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.geopolitical_contracts_id_seq', 1, false);


--
-- Name: guild_memberships_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.guild_memberships_id_seq', 1, false);


--
-- Name: guild_proposals_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.guild_proposals_id_seq', 1, false);


--
-- Name: infrastructure_resources_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.infrastructure_resources_id_seq', 1, false);


--
-- Name: insurance_claims_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.insurance_claims_id_seq', 1, false);


--
-- Name: insurance_policies_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.insurance_policies_id_seq', 1, false);


--
-- Name: insurance_premium_payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.insurance_premium_payments_id_seq', 1, false);


--
-- Name: intelligence_reports_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.intelligence_reports_id_seq', 1, false);


--
-- Name: marketplace_listings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.marketplace_listings_id_seq', 1, false);


--
-- Name: payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payments_id_seq', 1, false);


--
-- Name: posts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.posts_id_seq', 1, false);


--
-- Name: quantum_jobs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.quantum_jobs_id_seq', 1, false);


--
-- Name: sanction_targets_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sanction_targets_id_seq', 1, false);


--
-- Name: satellite_intelligence_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.satellite_intelligence_id_seq', 1, false);


--
-- Name: scans_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.scans_id_seq', 1, false);


--
-- Name: security_credit_scores_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.security_credit_scores_id_seq', 1, false);


--
-- Name: security_score_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.security_score_history_id_seq', 1, false);


--
-- Name: security_score_reports_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.security_score_reports_id_seq', 1, false);


--
-- Name: security_score_subscriptions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.security_score_subscriptions_id_seq', 1, false);


--
-- Name: security_scores_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.security_scores_id_seq', 1, false);


--
-- Name: self_healing_events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.self_healing_events_id_seq', 1, false);


--
-- Name: social_connections_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.social_connections_id_seq', 1, false);


--
-- Name: students_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.students_id_seq', 1, false);


--
-- Name: subscription_boxes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.subscription_boxes_id_seq', 1, false);


--
-- Name: subscriptions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.subscriptions_id_seq', 1, false);


--
-- Name: university_partnerships_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.university_partnerships_id_seq', 1, false);


--
-- Name: user_profiles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_profiles_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 1, false);


--
-- Name: vulnerability_forecasts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.vulnerability_forecasts_id_seq', 1, false);


--
-- Name: vulnerability_patterns_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.vulnerability_patterns_id_seq', 1, false);


--
-- Name: agi_research_logs agi_research_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agi_research_logs
    ADD CONSTRAINT agi_research_logs_pkey PRIMARY KEY (id);


--
-- Name: bci_security_audits bci_security_audits_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bci_security_audits
    ADD CONSTRAINT bci_security_audits_pkey PRIMARY KEY (id);


--
-- Name: bug_derivatives bug_derivatives_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_derivatives
    ADD CONSTRAINT bug_derivatives_pkey PRIMARY KEY (id);


--
-- Name: bug_future_positions bug_future_positions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_future_positions
    ADD CONSTRAINT bug_future_positions_pkey PRIMARY KEY (id);


--
-- Name: bug_futures_extended bug_futures_extended_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_futures_extended
    ADD CONSTRAINT bug_futures_extended_pkey PRIMARY KEY (id);


--
-- Name: bug_futures_old bug_futures_old_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_futures_old
    ADD CONSTRAINT bug_futures_old_pkey PRIMARY KEY (id);


--
-- Name: bug_index_funds bug_index_funds_fund_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_index_funds
    ADD CONSTRAINT bug_index_funds_fund_name_key UNIQUE (fund_name);


--
-- Name: bug_index_funds bug_index_funds_fund_symbol_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_index_funds
    ADD CONSTRAINT bug_index_funds_fund_symbol_key UNIQUE (fund_symbol);


--
-- Name: bug_index_funds bug_index_funds_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_index_funds
    ADD CONSTRAINT bug_index_funds_pkey PRIMARY KEY (id);


--
-- Name: bug_marketplace_listings bug_marketplace_listings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_marketplace_listings
    ADD CONSTRAINT bug_marketplace_listings_pkey PRIMARY KEY (id);


--
-- Name: bug_marketplace_trades bug_marketplace_trades_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_marketplace_trades
    ADD CONSTRAINT bug_marketplace_trades_pkey PRIMARY KEY (id);


--
-- Name: bug_nfts bug_nfts_bug_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_nfts
    ADD CONSTRAINT bug_nfts_bug_id_key UNIQUE (bug_id);


--
-- Name: bug_nfts bug_nfts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_nfts
    ADD CONSTRAINT bug_nfts_pkey PRIMARY KEY (id);


--
-- Name: bug_nfts bug_nfts_token_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_nfts
    ADD CONSTRAINT bug_nfts_token_id_key UNIQUE (token_id);


--
-- Name: bugs bugs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bugs
    ADD CONSTRAINT bugs_pkey PRIMARY KEY (id);


--
-- Name: comments comments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_pkey PRIMARY KEY (id);


--
-- Name: cost_optimization_recommendations cost_optimization_recommendations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_optimization_recommendations
    ADD CONSTRAINT cost_optimization_recommendations_pkey PRIMARY KEY (id);


--
-- Name: courses courses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_pkey PRIMARY KEY (id);


--
-- Name: creator_subscriptions creator_subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.creator_subscriptions
    ADD CONSTRAINT creator_subscriptions_pkey PRIMARY KEY (id);


--
-- Name: dao_governance_extended dao_governance_extended_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dao_governance_extended
    ADD CONSTRAINT dao_governance_extended_pkey PRIMARY KEY (id);


--
-- Name: dao_governance_old dao_governance_old_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dao_governance_old
    ADD CONSTRAINT dao_governance_old_pkey PRIMARY KEY (id);


--
-- Name: dao_governance_old dao_governance_old_token_symbol_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dao_governance_old
    ADD CONSTRAINT dao_governance_old_token_symbol_key UNIQUE (token_symbol);


--
-- Name: dao_proposals dao_proposals_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dao_proposals
    ADD CONSTRAINT dao_proposals_pkey PRIMARY KEY (id);


--
-- Name: dao_tokens dao_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dao_tokens
    ADD CONSTRAINT dao_tokens_pkey PRIMARY KEY (id);


--
-- Name: dao_treasury_transactions dao_treasury_transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dao_treasury_transactions
    ADD CONSTRAINT dao_treasury_transactions_pkey PRIMARY KEY (id);


--
-- Name: dao_votes dao_votes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dao_votes
    ADD CONSTRAINT dao_votes_pkey PRIMARY KEY (id);


--
-- Name: deployment_executions deployment_executions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deployment_executions
    ADD CONSTRAINT deployment_executions_pkey PRIMARY KEY (id);


--
-- Name: deployment_pipelines deployment_pipelines_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deployment_pipelines
    ADD CONSTRAINT deployment_pipelines_pkey PRIMARY KEY (id);


--
-- Name: devops_automation_jobs devops_automation_jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.devops_automation_jobs
    ADD CONSTRAINT devops_automation_jobs_pkey PRIMARY KEY (id);


--
-- Name: esg_scores esg_scores_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.esg_scores
    ADD CONSTRAINT esg_scores_pkey PRIMARY KEY (id);


--
-- Name: exploit_chains exploit_chains_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exploit_chains
    ADD CONSTRAINT exploit_chains_pkey PRIMARY KEY (id);


--
-- Name: exploit_database exploit_database_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exploit_database
    ADD CONSTRAINT exploit_database_pkey PRIMARY KEY (id);


--
-- Name: fix_offers fix_offers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fix_offers
    ADD CONSTRAINT fix_offers_pkey PRIMARY KEY (id);


--
-- Name: geopolitical_contracts geopolitical_contracts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.geopolitical_contracts
    ADD CONSTRAINT geopolitical_contracts_pkey PRIMARY KEY (id);


--
-- Name: guild_memberships guild_memberships_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.guild_memberships
    ADD CONSTRAINT guild_memberships_pkey PRIMARY KEY (id);


--
-- Name: guild_proposals guild_proposals_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.guild_proposals
    ADD CONSTRAINT guild_proposals_pkey PRIMARY KEY (id);


--
-- Name: infrastructure_resources infrastructure_resources_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.infrastructure_resources
    ADD CONSTRAINT infrastructure_resources_pkey PRIMARY KEY (id);


--
-- Name: insurance_claims insurance_claims_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.insurance_claims
    ADD CONSTRAINT insurance_claims_pkey PRIMARY KEY (id);


--
-- Name: insurance_policies insurance_policies_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.insurance_policies
    ADD CONSTRAINT insurance_policies_pkey PRIMARY KEY (id);


--
-- Name: insurance_premium_payments insurance_premium_payments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.insurance_premium_payments
    ADD CONSTRAINT insurance_premium_payments_pkey PRIMARY KEY (id);


--
-- Name: intelligence_reports intelligence_reports_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.intelligence_reports
    ADD CONSTRAINT intelligence_reports_pkey PRIMARY KEY (id);


--
-- Name: marketplace_listings marketplace_listings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.marketplace_listings
    ADD CONSTRAINT marketplace_listings_pkey PRIMARY KEY (id);


--
-- Name: payments payments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_pkey PRIMARY KEY (id);


--
-- Name: posts posts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_pkey PRIMARY KEY (id);


--
-- Name: quantum_jobs quantum_jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quantum_jobs
    ADD CONSTRAINT quantum_jobs_pkey PRIMARY KEY (id);


--
-- Name: sanction_targets sanction_targets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sanction_targets
    ADD CONSTRAINT sanction_targets_pkey PRIMARY KEY (id);


--
-- Name: satellite_intelligence satellite_intelligence_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.satellite_intelligence
    ADD CONSTRAINT satellite_intelligence_pkey PRIMARY KEY (id);


--
-- Name: scans scans_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scans
    ADD CONSTRAINT scans_pkey PRIMARY KEY (id);


--
-- Name: security_credit_scores security_credit_scores_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.security_credit_scores
    ADD CONSTRAINT security_credit_scores_pkey PRIMARY KEY (id);


--
-- Name: security_score_history security_score_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.security_score_history
    ADD CONSTRAINT security_score_history_pkey PRIMARY KEY (id);


--
-- Name: security_score_reports security_score_reports_access_token_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.security_score_reports
    ADD CONSTRAINT security_score_reports_access_token_key UNIQUE (access_token);


--
-- Name: security_score_reports security_score_reports_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.security_score_reports
    ADD CONSTRAINT security_score_reports_pkey PRIMARY KEY (id);


--
-- Name: security_score_subscriptions security_score_subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.security_score_subscriptions
    ADD CONSTRAINT security_score_subscriptions_pkey PRIMARY KEY (id);


--
-- Name: security_scores security_scores_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.security_scores
    ADD CONSTRAINT security_scores_pkey PRIMARY KEY (id);


--
-- Name: self_healing_events self_healing_events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.self_healing_events
    ADD CONSTRAINT self_healing_events_pkey PRIMARY KEY (id);


--
-- Name: social_connections social_connections_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.social_connections
    ADD CONSTRAINT social_connections_pkey PRIMARY KEY (id);


--
-- Name: students students_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_pkey PRIMARY KEY (id);


--
-- Name: students students_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_user_id_key UNIQUE (user_id);


--
-- Name: subscription_boxes subscription_boxes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscription_boxes
    ADD CONSTRAINT subscription_boxes_pkey PRIMARY KEY (id);


--
-- Name: subscriptions subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_pkey PRIMARY KEY (id);


--
-- Name: university_partnerships university_partnerships_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.university_partnerships
    ADD CONSTRAINT university_partnerships_pkey PRIMARY KEY (id);


--
-- Name: university_partnerships university_partnerships_university_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.university_partnerships
    ADD CONSTRAINT university_partnerships_university_code_key UNIQUE (university_code);


--
-- Name: university_partnerships university_partnerships_university_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.university_partnerships
    ADD CONSTRAINT university_partnerships_university_name_key UNIQUE (university_name);


--
-- Name: user_profiles user_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_profiles
    ADD CONSTRAINT user_profiles_pkey PRIMARY KEY (id);


--
-- Name: user_profiles user_profiles_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_profiles
    ADD CONSTRAINT user_profiles_user_id_key UNIQUE (user_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: vulnerability_forecasts vulnerability_forecasts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vulnerability_forecasts
    ADD CONSTRAINT vulnerability_forecasts_pkey PRIMARY KEY (id);


--
-- Name: vulnerability_patterns vulnerability_patterns_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vulnerability_patterns
    ADD CONSTRAINT vulnerability_patterns_pkey PRIMARY KEY (id);


--
-- Name: ix_agi_research_logs_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_agi_research_logs_id ON public.agi_research_logs USING btree (id);


--
-- Name: ix_bci_security_audits_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bci_security_audits_id ON public.bci_security_audits USING btree (id);


--
-- Name: ix_bug_derivatives_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bug_derivatives_id ON public.bug_derivatives USING btree (id);


--
-- Name: ix_bug_future_positions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bug_future_positions_id ON public.bug_future_positions USING btree (id);


--
-- Name: ix_bug_futures_extended_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bug_futures_extended_id ON public.bug_futures_extended USING btree (id);


--
-- Name: ix_bug_futures_old_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bug_futures_old_id ON public.bug_futures_old USING btree (id);


--
-- Name: ix_bug_index_funds_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bug_index_funds_id ON public.bug_index_funds USING btree (id);


--
-- Name: ix_bug_marketplace_listings_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bug_marketplace_listings_id ON public.bug_marketplace_listings USING btree (id);


--
-- Name: ix_bug_marketplace_trades_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bug_marketplace_trades_id ON public.bug_marketplace_trades USING btree (id);


--
-- Name: ix_bug_nfts_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bug_nfts_id ON public.bug_nfts USING btree (id);


--
-- Name: ix_bugs_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bugs_created_at ON public.bugs USING btree (created_at);


--
-- Name: ix_bugs_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bugs_id ON public.bugs USING btree (id);


--
-- Name: ix_bugs_target_domain; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bugs_target_domain ON public.bugs USING btree (target_domain);


--
-- Name: ix_comments_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_comments_id ON public.comments USING btree (id);


--
-- Name: ix_cost_optimization_recommendations_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cost_optimization_recommendations_id ON public.cost_optimization_recommendations USING btree (id);


--
-- Name: ix_courses_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_courses_id ON public.courses USING btree (id);


--
-- Name: ix_creator_subscriptions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_creator_subscriptions_id ON public.creator_subscriptions USING btree (id);


--
-- Name: ix_dao_governance_extended_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_dao_governance_extended_id ON public.dao_governance_extended USING btree (id);


--
-- Name: ix_dao_governance_old_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_dao_governance_old_id ON public.dao_governance_old USING btree (id);


--
-- Name: ix_dao_proposals_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_dao_proposals_id ON public.dao_proposals USING btree (id);


--
-- Name: ix_dao_proposals_proposal_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_dao_proposals_proposal_number ON public.dao_proposals USING btree (proposal_number);


--
-- Name: ix_dao_tokens_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_dao_tokens_id ON public.dao_tokens USING btree (id);


--
-- Name: ix_dao_treasury_transactions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_dao_treasury_transactions_id ON public.dao_treasury_transactions USING btree (id);


--
-- Name: ix_dao_votes_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_dao_votes_id ON public.dao_votes USING btree (id);


--
-- Name: ix_deployment_executions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_deployment_executions_id ON public.deployment_executions USING btree (id);


--
-- Name: ix_deployment_pipelines_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_deployment_pipelines_id ON public.deployment_pipelines USING btree (id);


--
-- Name: ix_devops_automation_jobs_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_devops_automation_jobs_id ON public.devops_automation_jobs USING btree (id);


--
-- Name: ix_esg_scores_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_esg_scores_id ON public.esg_scores USING btree (id);


--
-- Name: ix_exploit_chains_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_exploit_chains_id ON public.exploit_chains USING btree (id);


--
-- Name: ix_exploit_database_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_exploit_database_id ON public.exploit_database USING btree (id);


--
-- Name: ix_fix_offers_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_fix_offers_id ON public.fix_offers USING btree (id);


--
-- Name: ix_geopolitical_contracts_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_geopolitical_contracts_id ON public.geopolitical_contracts USING btree (id);


--
-- Name: ix_guild_memberships_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_guild_memberships_id ON public.guild_memberships USING btree (id);


--
-- Name: ix_guild_proposals_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_guild_proposals_id ON public.guild_proposals USING btree (id);


--
-- Name: ix_infrastructure_resources_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_infrastructure_resources_id ON public.infrastructure_resources USING btree (id);


--
-- Name: ix_insurance_claims_claim_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_insurance_claims_claim_number ON public.insurance_claims USING btree (claim_number);


--
-- Name: ix_insurance_claims_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_insurance_claims_id ON public.insurance_claims USING btree (id);


--
-- Name: ix_insurance_policies_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_insurance_policies_id ON public.insurance_policies USING btree (id);


--
-- Name: ix_insurance_policies_policy_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_insurance_policies_policy_number ON public.insurance_policies USING btree (policy_number);


--
-- Name: ix_insurance_premium_payments_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_insurance_premium_payments_id ON public.insurance_premium_payments USING btree (id);


--
-- Name: ix_intelligence_reports_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_intelligence_reports_id ON public.intelligence_reports USING btree (id);


--
-- Name: ix_marketplace_listings_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_marketplace_listings_id ON public.marketplace_listings USING btree (id);


--
-- Name: ix_payments_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_payments_id ON public.payments USING btree (id);


--
-- Name: ix_posts_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_posts_id ON public.posts USING btree (id);


--
-- Name: ix_quantum_jobs_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quantum_jobs_id ON public.quantum_jobs USING btree (id);


--
-- Name: ix_sanction_targets_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sanction_targets_id ON public.sanction_targets USING btree (id);


--
-- Name: ix_satellite_intelligence_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_satellite_intelligence_id ON public.satellite_intelligence USING btree (id);


--
-- Name: ix_scans_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_scans_created_at ON public.scans USING btree (created_at);


--
-- Name: ix_scans_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_scans_id ON public.scans USING btree (id);


--
-- Name: ix_scans_target_domain; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_scans_target_domain ON public.scans USING btree (target_domain);


--
-- Name: ix_security_credit_scores_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_security_credit_scores_id ON public.security_credit_scores USING btree (id);


--
-- Name: ix_security_score_history_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_security_score_history_id ON public.security_score_history USING btree (id);


--
-- Name: ix_security_score_reports_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_security_score_reports_id ON public.security_score_reports USING btree (id);


--
-- Name: ix_security_score_subscriptions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_security_score_subscriptions_id ON public.security_score_subscriptions USING btree (id);


--
-- Name: ix_security_scores_company_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_security_scores_company_name ON public.security_scores USING btree (company_name);


--
-- Name: ix_security_scores_domain; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_security_scores_domain ON public.security_scores USING btree (domain);


--
-- Name: ix_security_scores_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_security_scores_id ON public.security_scores USING btree (id);


--
-- Name: ix_self_healing_events_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_self_healing_events_id ON public.self_healing_events USING btree (id);


--
-- Name: ix_social_connections_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_social_connections_id ON public.social_connections USING btree (id);


--
-- Name: ix_students_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_students_id ON public.students USING btree (id);


--
-- Name: ix_subscription_boxes_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_subscription_boxes_id ON public.subscription_boxes USING btree (id);


--
-- Name: ix_subscriptions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_subscriptions_id ON public.subscriptions USING btree (id);


--
-- Name: ix_university_partnerships_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_university_partnerships_id ON public.university_partnerships USING btree (id);


--
-- Name: ix_user_profiles_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_profiles_id ON public.user_profiles USING btree (id);


--
-- Name: ix_users_api_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_api_key ON public.users USING btree (api_key);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: ix_vulnerability_forecasts_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_vulnerability_forecasts_id ON public.vulnerability_forecasts USING btree (id);


--
-- Name: ix_vulnerability_patterns_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_vulnerability_patterns_id ON public.vulnerability_patterns USING btree (id);


--
-- Name: bci_security_audits bci_security_audits_auditor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bci_security_audits
    ADD CONSTRAINT bci_security_audits_auditor_id_fkey FOREIGN KEY (auditor_id) REFERENCES public.users(id);


--
-- Name: bug_derivatives bug_derivatives_buyer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_derivatives
    ADD CONSTRAINT bug_derivatives_buyer_id_fkey FOREIGN KEY (buyer_id) REFERENCES public.users(id);


--
-- Name: bug_derivatives bug_derivatives_seller_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_derivatives
    ADD CONSTRAINT bug_derivatives_seller_id_fkey FOREIGN KEY (seller_id) REFERENCES public.users(id);


--
-- Name: bug_future_positions bug_future_positions_future_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_future_positions
    ADD CONSTRAINT bug_future_positions_future_id_fkey FOREIGN KEY (future_id) REFERENCES public.bug_futures_extended(id);


--
-- Name: bug_future_positions bug_future_positions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_future_positions
    ADD CONSTRAINT bug_future_positions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: bug_futures_extended bug_futures_extended_creator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_futures_extended
    ADD CONSTRAINT bug_futures_extended_creator_id_fkey FOREIGN KEY (creator_id) REFERENCES public.users(id);


--
-- Name: bug_futures_old bug_futures_old_bug_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_futures_old
    ADD CONSTRAINT bug_futures_old_bug_id_fkey FOREIGN KEY (bug_id) REFERENCES public.bugs(id);


--
-- Name: bug_futures_old bug_futures_old_buyer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_futures_old
    ADD CONSTRAINT bug_futures_old_buyer_id_fkey FOREIGN KEY (buyer_id) REFERENCES public.users(id);


--
-- Name: bug_marketplace_listings bug_marketplace_listings_bug_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_marketplace_listings
    ADD CONSTRAINT bug_marketplace_listings_bug_id_fkey FOREIGN KEY (bug_id) REFERENCES public.bugs(id);


--
-- Name: bug_marketplace_listings bug_marketplace_listings_seller_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_marketplace_listings
    ADD CONSTRAINT bug_marketplace_listings_seller_id_fkey FOREIGN KEY (seller_id) REFERENCES public.users(id);


--
-- Name: bug_marketplace_trades bug_marketplace_trades_buyer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_marketplace_trades
    ADD CONSTRAINT bug_marketplace_trades_buyer_id_fkey FOREIGN KEY (buyer_id) REFERENCES public.users(id);


--
-- Name: bug_marketplace_trades bug_marketplace_trades_listing_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_marketplace_trades
    ADD CONSTRAINT bug_marketplace_trades_listing_id_fkey FOREIGN KEY (listing_id) REFERENCES public.bug_marketplace_listings(id);


--
-- Name: bug_marketplace_trades bug_marketplace_trades_seller_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_marketplace_trades
    ADD CONSTRAINT bug_marketplace_trades_seller_id_fkey FOREIGN KEY (seller_id) REFERENCES public.users(id);


--
-- Name: bug_nfts bug_nfts_bug_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_nfts
    ADD CONSTRAINT bug_nfts_bug_id_fkey FOREIGN KEY (bug_id) REFERENCES public.bugs(id);


--
-- Name: bug_nfts bug_nfts_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_nfts
    ADD CONSTRAINT bug_nfts_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id);


--
-- Name: bugs bugs_hunter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bugs
    ADD CONSTRAINT bugs_hunter_id_fkey FOREIGN KEY (hunter_id) REFERENCES public.users(id);


--
-- Name: bugs bugs_scan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bugs
    ADD CONSTRAINT bugs_scan_id_fkey FOREIGN KEY (scan_id) REFERENCES public.scans(id);


--
-- Name: comments comments_parent_comment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_parent_comment_id_fkey FOREIGN KEY (parent_comment_id) REFERENCES public.comments(id);


--
-- Name: comments comments_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.posts(id);


--
-- Name: comments comments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: cost_optimization_recommendations cost_optimization_recommendations_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_optimization_recommendations
    ADD CONSTRAINT cost_optimization_recommendations_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.users(id);


--
-- Name: cost_optimization_recommendations cost_optimization_recommendations_resource_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cost_optimization_recommendations
    ADD CONSTRAINT cost_optimization_recommendations_resource_id_fkey FOREIGN KEY (resource_id) REFERENCES public.infrastructure_resources(id);


--
-- Name: courses courses_instructor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_instructor_id_fkey FOREIGN KEY (instructor_id) REFERENCES public.users(id);


--
-- Name: creator_subscriptions creator_subscriptions_creator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.creator_subscriptions
    ADD CONSTRAINT creator_subscriptions_creator_id_fkey FOREIGN KEY (creator_id) REFERENCES public.users(id);


--
-- Name: creator_subscriptions creator_subscriptions_subscriber_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.creator_subscriptions
    ADD CONSTRAINT creator_subscriptions_subscriber_id_fkey FOREIGN KEY (subscriber_id) REFERENCES public.users(id);


--
-- Name: dao_proposals dao_proposals_executed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dao_proposals
    ADD CONSTRAINT dao_proposals_executed_by_fkey FOREIGN KEY (executed_by) REFERENCES public.users(id);


--
-- Name: dao_proposals dao_proposals_proposer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dao_proposals
    ADD CONSTRAINT dao_proposals_proposer_id_fkey FOREIGN KEY (proposer_id) REFERENCES public.users(id);


--
-- Name: dao_tokens dao_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dao_tokens
    ADD CONSTRAINT dao_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: dao_treasury_transactions dao_treasury_transactions_proposal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dao_treasury_transactions
    ADD CONSTRAINT dao_treasury_transactions_proposal_id_fkey FOREIGN KEY (proposal_id) REFERENCES public.dao_proposals(id);


--
-- Name: dao_votes dao_votes_proposal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dao_votes
    ADD CONSTRAINT dao_votes_proposal_id_fkey FOREIGN KEY (proposal_id) REFERENCES public.dao_proposals(id);


--
-- Name: dao_votes dao_votes_voter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dao_votes
    ADD CONSTRAINT dao_votes_voter_id_fkey FOREIGN KEY (voter_id) REFERENCES public.users(id);


--
-- Name: deployment_executions deployment_executions_pipeline_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deployment_executions
    ADD CONSTRAINT deployment_executions_pipeline_id_fkey FOREIGN KEY (pipeline_id) REFERENCES public.deployment_pipelines(id);


--
-- Name: deployment_executions deployment_executions_triggered_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deployment_executions
    ADD CONSTRAINT deployment_executions_triggered_by_fkey FOREIGN KEY (triggered_by) REFERENCES public.users(id);


--
-- Name: deployment_pipelines deployment_pipelines_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deployment_pipelines
    ADD CONSTRAINT deployment_pipelines_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.users(id);


--
-- Name: devops_automation_jobs devops_automation_jobs_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.devops_automation_jobs
    ADD CONSTRAINT devops_automation_jobs_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.users(id);


--
-- Name: devops_automation_jobs devops_automation_jobs_triggered_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.devops_automation_jobs
    ADD CONSTRAINT devops_automation_jobs_triggered_by_fkey FOREIGN KEY (triggered_by) REFERENCES public.users(id);


--
-- Name: fix_offers fix_offers_bug_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fix_offers
    ADD CONSTRAINT fix_offers_bug_id_fkey FOREIGN KEY (bug_id) REFERENCES public.bugs(id);


--
-- Name: fix_offers fix_offers_developer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fix_offers
    ADD CONSTRAINT fix_offers_developer_id_fkey FOREIGN KEY (developer_id) REFERENCES public.users(id);


--
-- Name: guild_memberships guild_memberships_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.guild_memberships
    ADD CONSTRAINT guild_memberships_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: guild_proposals guild_proposals_proposer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.guild_proposals
    ADD CONSTRAINT guild_proposals_proposer_id_fkey FOREIGN KEY (proposer_id) REFERENCES public.users(id);


--
-- Name: infrastructure_resources infrastructure_resources_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.infrastructure_resources
    ADD CONSTRAINT infrastructure_resources_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.users(id);


--
-- Name: infrastructure_resources infrastructure_resources_provisioned_by_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.infrastructure_resources
    ADD CONSTRAINT infrastructure_resources_provisioned_by_job_id_fkey FOREIGN KEY (provisioned_by_job_id) REFERENCES public.devops_automation_jobs(id);


--
-- Name: insurance_claims insurance_claims_bug_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.insurance_claims
    ADD CONSTRAINT insurance_claims_bug_id_fkey FOREIGN KEY (bug_id) REFERENCES public.bugs(id);


--
-- Name: insurance_claims insurance_claims_policy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.insurance_claims
    ADD CONSTRAINT insurance_claims_policy_id_fkey FOREIGN KEY (policy_id) REFERENCES public.insurance_policies(id);


--
-- Name: insurance_claims insurance_claims_reviewed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.insurance_claims
    ADD CONSTRAINT insurance_claims_reviewed_by_fkey FOREIGN KEY (reviewed_by) REFERENCES public.users(id);


--
-- Name: insurance_policies insurance_policies_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.insurance_policies
    ADD CONSTRAINT insurance_policies_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.users(id);


--
-- Name: insurance_premium_payments insurance_premium_payments_policy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.insurance_premium_payments
    ADD CONSTRAINT insurance_premium_payments_policy_id_fkey FOREIGN KEY (policy_id) REFERENCES public.insurance_policies(id);


--
-- Name: intelligence_reports intelligence_reports_buyer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.intelligence_reports
    ADD CONSTRAINT intelligence_reports_buyer_id_fkey FOREIGN KEY (buyer_id) REFERENCES public.users(id);


--
-- Name: marketplace_listings marketplace_listings_bug_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.marketplace_listings
    ADD CONSTRAINT marketplace_listings_bug_id_fkey FOREIGN KEY (bug_id) REFERENCES public.bugs(id);


--
-- Name: marketplace_listings marketplace_listings_seller_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.marketplace_listings
    ADD CONSTRAINT marketplace_listings_seller_id_fkey FOREIGN KEY (seller_id) REFERENCES public.users(id);


--
-- Name: payments payments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: posts posts_bug_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_bug_id_fkey FOREIGN KEY (bug_id) REFERENCES public.bugs(id);


--
-- Name: posts posts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: quantum_jobs quantum_jobs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quantum_jobs
    ADD CONSTRAINT quantum_jobs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: scans scans_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scans
    ADD CONSTRAINT scans_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: security_credit_scores security_credit_scores_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.security_credit_scores
    ADD CONSTRAINT security_credit_scores_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.users(id);


--
-- Name: security_score_history security_score_history_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.security_score_history
    ADD CONSTRAINT security_score_history_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.users(id);


--
-- Name: security_score_reports security_score_reports_generated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.security_score_reports
    ADD CONSTRAINT security_score_reports_generated_by_fkey FOREIGN KEY (generated_by) REFERENCES public.users(id);


--
-- Name: security_score_reports security_score_reports_purchased_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.security_score_reports
    ADD CONSTRAINT security_score_reports_purchased_by_fkey FOREIGN KEY (purchased_by) REFERENCES public.users(id);


--
-- Name: security_score_reports security_score_reports_score_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.security_score_reports
    ADD CONSTRAINT security_score_reports_score_id_fkey FOREIGN KEY (score_id) REFERENCES public.security_scores(id);


--
-- Name: security_score_subscriptions security_score_subscriptions_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.security_score_subscriptions
    ADD CONSTRAINT security_score_subscriptions_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.users(id);


--
-- Name: security_score_subscriptions security_score_subscriptions_subscriber_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.security_score_subscriptions
    ADD CONSTRAINT security_score_subscriptions_subscriber_id_fkey FOREIGN KEY (subscriber_id) REFERENCES public.users(id);


--
-- Name: security_scores security_scores_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.security_scores
    ADD CONSTRAINT security_scores_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.users(id);


--
-- Name: self_healing_events self_healing_events_resource_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.self_healing_events
    ADD CONSTRAINT self_healing_events_resource_id_fkey FOREIGN KEY (resource_id) REFERENCES public.infrastructure_resources(id);


--
-- Name: social_connections social_connections_connected_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.social_connections
    ADD CONSTRAINT social_connections_connected_user_id_fkey FOREIGN KEY (connected_user_id) REFERENCES public.users(id);


--
-- Name: social_connections social_connections_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.social_connections
    ADD CONSTRAINT social_connections_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: students students_university_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_university_id_fkey FOREIGN KEY (university_id) REFERENCES public.university_partnerships(id);


--
-- Name: students students_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: subscription_boxes subscription_boxes_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscription_boxes
    ADD CONSTRAINT subscription_boxes_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

\unrestrict vURxlRZzOxGQEigwI2uLsOPkPXJqvPbnfTS4FD2spTkvtZkHnVBr6OORdRE0xY1

