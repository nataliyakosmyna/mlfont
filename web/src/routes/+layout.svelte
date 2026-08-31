<script lang="ts">
  import { assets } from '$app/paths';
  import { absoluteUrl, siteUrl } from '$lib/site';

  let { children } = $props();

  const SITE = 'MIT Media Lab Font';
  const DESC =
    'A 7×7 grid typeface in the spirit of the Media Lab generative identity. Six weights, TTF + OTF.';

  const ogImage = absoluteUrl('/og.png');
  const canonicalUrl = siteUrl ? `${siteUrl}/` : undefined;
</script>

<svelte:head>
  <meta name="description" content={DESC} />
  <meta name="theme-color" content="#0a0a0a" media="(prefers-color-scheme: dark)" />
  <meta name="theme-color" content="#ece8de" media="(prefers-color-scheme: light)" />

  <meta property="og:type" content="website" />
  <meta property="og:title" content={SITE} />
  <meta property="og:description" content={DESC} />
  {#if canonicalUrl}
    <meta property="og:url" content={canonicalUrl} />
    <link rel="canonical" href={canonicalUrl} />
  {/if}
  <meta property="og:image" content={ogImage} />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="MIT Media Lab Font — MIT wordmark and Media Lab mark" />

  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content={SITE} />
  <meta name="twitter:description" content={DESC} />
  <meta name="twitter:image" content={ogImage} />

  <link rel="icon" href="{assets}/favicon.svg" type="image/svg+xml" />
  <link rel="icon" href="{assets}/favicon.png" type="image/png" sizes="32x32" />
  <link rel="apple-touch-icon" href="{assets}/apple-touch-icon.png" />
</svelte:head>

{@render children()}
