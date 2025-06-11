function update_image() {

    // Set halo index
    const index = document.getElementById('index').value;

    // Select FoF / central / satellite particles
    let particles = null;
    if(document.getElementById('fof').checked)particles = "fof";
    if(document.getElementById('central').checked)particles = "central";
    if(document.getElementById('satellite').checked)particles = "satellites";

    // Select code branch
    let branch = null;
    if(document.getElementById('default').checked)branch = "default";
    if(document.getElementById('reassign').checked)branch = "reassign_gas_multi_fixed";
    if(document.getElementById('spatial').checked)branch = "reassign_gas_multi_fixed_spatial_nest";

    // Select component
    let component = null;
    if(document.getElementById('stars').checked)component = "stars";
    if(document.getElementById('dm').checked)component = "dark_matter";

    // Update the image
    if((particles != null) && (branch != null) && (component != null)) {
	const filename = "images/"+branch+"/"+particles+"_"+component+"_0123_halo_"+index+".png"
	document.getElementById('image').src = filename;
    } else {
	document.getElementById('image').src = "";
    }
}

const all_ids = ["index", "fof", "central", "satellite", "default", "reassign", "spatial", "stars", "dm"]
all_ids.forEach((name) => {
    document.getElementById(name).addEventListener('input', (event) => {
	update_image();
    });
});

update_image();
