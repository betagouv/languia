<script context="module">
	let _id = 0;
</script>

<script lang="ts">
	import "@gouvfr/dsfr/dist/scheme/scheme.css";
	import "@gouvfr/dsfr/dist/core/core.css";
	import "@gouvfr/dsfr/dist/component/form/form.css";
	import "@gouvfr/dsfr/dist/component/link/link.css";
	import "@gouvfr/dsfr/dist/component/button/button.css";
	import "@gouvfr/dsfr/dist/component/input/input.css";
	import "@gouvfr/dsfr/dist/component/range/range.css";

	import type { Gradio } from "@gradio/utils";
	import { Block, BlockTitle } from "@gradio/atoms";
	import { StatusTracker } from "@gradio/statustracker";
	import type { LoadingStatus } from "@gradio/statustracker";
	import { afterUpdate } from "svelte";

	export let gradio: Gradio<{
		change: never;
		input: never;
		release: number;
		clear_status: LoadingStatus;
	}>;
	export let elem_id = "";
	export let elem_classes: string[] = [];
	export let visible = true;
	export let value = 0;
	export let label = gradio.i18n("slider.slider");
	export let info: string | undefined = undefined;
	// export let container = true;
	// export let scale: number | null = null;
	// export let min_width: number | undefined = undefined;
	export let range_labels: string[] = [];
	export let minimum: number;
	export let maximum = 100;
	export let step: number;
	export let show_label: boolean;
	export let interactive: boolean;
	export let loading_status: LoadingStatus;
	export let value_is_output = false;

	let currentLabel: number;
	let labelIndex: number;
	let rangeInput: HTMLInputElement;
	// let numberInput: HTMLInputElement;

	const id = `range_id_${_id++}`;

	function handle_change(): void {
		gradio.dispatch("change");
		if (!value_is_output) {
			gradio.dispatch("input");
		}
	}
	afterUpdate(() => {
		value_is_output = false;
		setSlider();
	});

	function handle_release(e: MouseEvent): void {
		gradio.dispatch("release", value);
	}
	function clamp(): void {
		gradio.dispatch("release", value);
		value = Math.min(Math.max(value, minimum), maximum);
	}

	function setSlider(): void {
		setSliderRange();
		rangeInput.addEventListener("input", setSliderRange);
	}
	function setSliderRange(): void {
		const dividend = Number(rangeInput.value) - Number(rangeInput.min);
		const divisor = Number(rangeInput.max) - Number(rangeInput.min);
		const h = divisor === 0 ? 0 : dividend / divisor;
		rangeInput.style.backgroundSize = h * 100 + "% 100%";
	}


	$: disabled = !interactive;

	// When the value changes, dispatch the change event via handle_change()
	// See the docs for an explanation: https://svelte.dev/docs/svelte-components#script-3-$-marks-a-statement-as-reactive
	$: value, handle_change();
</script>

<div id={elem_id} class="{elem_classes} {visible ? '' : 'hide'}">
	<StatusTracker
		autoscroll={gradio.autoscroll}
		i18n={gradio.i18n}
		{...loading_status}
		on:clear_status={() => gradio.dispatch("clear_status", loading_status)}
	/>
	<label class="fr-label" for={id}>
		{#if show_label}
			{label}
			<span class="fr-hint-text">{info}</span>
		{/if}
	</label>

	<div class="fr-range-group">
		<div class="fr-range fr-range--step" data-fr-js-range="true">

			<span class="fr-range__output">{value}</span
			>
			<input
				type="range"
				{id}
				name={id}
				bind:value
				bind:this={rangeInput}
				min={minimum}
				max={maximum}
				{step}
				{disabled}
				on:pointerup={handle_release}
				aria-label={`range slider for ${label}`}
			/>
			{#if range_labels.length != 0}
				{#each range_labels as range_label, labelIndex}
					<span
						class="fr-range__custom-label">{range_label}</span
					>
				{/each}
			{:else}
				<span class="fr-range__min" aria-hidden="true">{minimum}</span>
				<span class="fr-range__max" aria-hidden="true">{maximum}</span>
			{/if}
		</div>
	</div>
</div>

<style>
	
	.fr-label {
		font-size: 1.175rem;
  		font-weight: 700;
	}
	.fr-hint-text {
		font-weight: 400;
		font-size: 1rem;
	}
		
	input:disabled {
		-webkit-text-fill-color: var(--body-text-color);
		-webkit-opacity: 1;
		opacity: 1;
	}

	input[disabled] {
		cursor: not-allowed;
	}

</style>
