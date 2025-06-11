function update_image(config) {

    let snap_nr = String(config["snap_nr"]).padStart(4, '0');

    // Set halo index
    const index = document.getElementById('halo_nr').value;

    // Select FoF / central / satellite particles
    let particles = null;
    if(document.getElementById('fof').checked)particles = "fof";
    if(document.getElementById('central').checked)particles = "central";
    if(document.getElementById('satellite').checked)particles = "satellites";

    // Select code branch
    let branch = "null";
    Object.keys(config["branches"]).forEach(name => {
        const id = "branch_"+name;
        if(document.getElementById(id).checked)branch = name;
    });

    // Select component
    let component = null;
    config["ptypes"].forEach((name, index) => {
        const id = "component_"+name;
        if(document.getElementById(id).checked)component = name;
    });

    // Update the image
    if((particles != null) && (branch != null) && (component != null)) {
	const filename = branch+"/"+particles+"_"+component+"_"+snap_nr+"_halo_"+index+".png"
	document.getElementById('image').src = filename;
    } else {
	document.getElementById('image').src = "";
    }
}


function setup_page(config) {

    let all_ids = ["fof","central","satellite"];

    // Set up numeric input for halo index
    const halo_nr_input = document.getElementById("halo_nr");
    halo_nr_input.min = "0";
    halo_nr_input.max = (config.nr_halos - 1);
    halo_nr_input.step = "1";
    halo_nr_input.value = "0";
    all_ids.push(halo_nr_input.id);

    // Create a radio button for each code branch
    const branch_div = document.getElementById("branch");
    let first = 1;
    Object.keys(config["branches"]).forEach(name => {

        // Create the button
        const input = document.createElement("input");
        input.type = "radio";
        input.name = "branch_input";
        input.value = name;
        input.id   = "branch_"+name;
        if(first) {
            input.checked = "checked";
            first = 0;
        }
        all_ids.push(input.id);

        // Add a label
        const label = document.createElement("label");
        label.htmlFor = input.id;
        label.textContent = name;

        // Append to the container
        branch_div.appendChild(input);
        branch_div.appendChild(label);
        branch_div.appendChild(document.createElement("br"));

    });

    // Create a radio button for each particle type
    const component_div = document.getElementById("component");
    config["ptypes"].forEach((name, index) => {

        // Create the button
        const input = document.createElement("input");
        input.type = "radio";
        input.name = "component_input";
        input.value = name;
        input.id   = "component_"+name;
        if(index==0)input.checked = "checked";
        all_ids.push(input.id);

        // Add a label
        const label = document.createElement("label");
        label.htmlFor = input.id;
        label.textContent = name;

        // Append to the container
        component_div.appendChild(input);
        component_div.appendChild(label);
        component_div.appendChild(document.createElement("br"));

    });

    // Update image if any of the inputs change
    all_ids.forEach((name) => {
        document.getElementById(name).addEventListener('input', (event) => {
	    update_image(config);
        });
    });
}

fetch("params.json")
    .then(response => response.json())
    .then(config => {setup_page(config); update_image(config);});
