<script>
	import '@evidence-dev/tailwind/fonts.css';
	import '../app.css';
	import { EvidenceDefaultLayout } from '@evidence-dev/core-components';
	export let data;
</script>

<!-- A single page needs no sidebar, breadcrumbs or query viewers. -->
<EvidenceDefaultLayout
	{data}
	title="Ladeinfrastruktur"
	hideSidebar
	hideBreadcrumbs
	hideTOC
	neverShowQueries
	builtWithEvidence={false}
	maxWidth="1280"
>
	<slot slot="content" />
</EvidenceDefaultLayout>
