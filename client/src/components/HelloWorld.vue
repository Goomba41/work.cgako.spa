<template>
  <div class="hello">
    <h1>{{ msg }}</h1>
    <p>
      For a guide and recipes on how to configure / customize this project,<br>
      check out the
      <a href="https://cli.vuejs.org" target="_blank" rel="noopener">vue-cli documentation</a>.
    </p>
    <h3>Installed CLI Plugins</h3>
    <ul>
      <li><a href="https://github.com/vuejs/vue-cli/tree/dev/packages/%40vue/cli-plugin-babel" target="_blank" rel="noopener">babel</a></li>
      <li><a href="https://github.com/vuejs/vue-cli/tree/dev/packages/%40vue/cli-plugin-eslint" target="_blank" rel="noopener">eslint</a></li>
    </ul>
    <h3>Essential Links</h3>
    <ul>
      <li><a href="https://vuejs.org" target="_blank" rel="noopener">Core Docs</a></li>
      <li><a href="https://forum.vuejs.org" target="_blank" rel="noopener">Forum</a></li>
      <li><a href="https://chat.vuejs.org" target="_blank" rel="noopener">Community Chat</a></li>
      <li><a href="https://twitter.com/vuejs" target="_blank" rel="noopener">Twitter</a></li>
      <li><a href="https://news.vuejs.org" target="_blank" rel="noopener">News</a></li>
    </ul>
    <h3>Ecosystem</h3>
    <ul>
      <li><a href="https://router.vuejs.org" target="_blank" rel="noopener">vue-router</a></li>
      <li><a href="https://vuex.vuejs.org" target="_blank" rel="noopener">vuex</a></li>
      <li><a href="https://github.com/vuejs/vue-devtools#vue-devtools" target="_blank" rel="noopener">vue-devtools</a></li>
      <li><a href="https://vue-loader.vuejs.org" target="_blank" rel="noopener">vue-loader</a></li>
      <li><a href="https://github.com/vuejs/awesome-vue" target="_blank" rel="noopener">awesome-vue</a></li>
    </ul>
    <div>
      <button @click="addNode">Add Node</button>
      <vue-tree-list
        @click="onClick"
        @change-name="onChangeName"
        @delete-node="onDel"
        @add-node="onAddNode"
        @drop="onDrop"
        @drop-before="onDropBefore"
        @drop-after="onDropAfter"
        :model="data"
        default-tree-node-name="new node"
        default-leaf-node-name="new leaf"
        v-bind:default-expanded="false"
      >
        <template v-slot:leafNameDisplay="slotProps">
          <span>
            {{ slotProps.model.name }} <span class="muted">#{{ slotProps.model.id }}</span>
          </span>
        </template>
        <span class="icon" slot="addTreeNodeIcon">📂</span>
        <span class="icon" slot="addLeafNodeIcon">＋</span>
        <span class="icon" slot="editNodeIcon">📃</span>
        <span class="icon" slot="delNodeIcon">✂️</span>
        <span class="icon" slot="leafNodeIcon">🍃</span>
        <span class="icon" slot="treeNodeIcon">🌲</span>
      </vue-tree-list>
      <button @click="getNewTree">Get new tree</button>
      <pre>
        {{newTree}}
      </pre>
    </div>

  </div>
</template>

<script>
import { VueTreeList, Tree, TreeNode } from 'vue-tree-list'
export default {
  name: 'HelloWorld',
  components: {
    VueTreeList
  },
  props: {
    msg: String
  },
  data() {
    return {
      newTree: {},
      data: new Tree([
        {
          name: 'Node 1',
          id: 1,
          pid: 0,
          dragDisabled: true,
          addTreeNodeDisabled: true,
          addLeafNodeDisabled: true,
          editNodeDisabled: true,
          delNodeDisabled: true,
          children: [
            {
              name: 'Node 1-2',
              id: 2,
              isLeaf: true,
              pid: 1
            }
          ]
        },
        {
          name: 'Node 2',
          id: 3,
          pid: 0,
          disabled: true
        },
        {
          name: 'Node 3',
          id: 4,
          pid: 0
        }
      ])
    }
  },
  methods: {
    onDrop(node){
      console.log('into ' + node.target.id);
    },

    onDropBefore(node){
      console.log('before ' + node.target.id);
    },

    onDropAfter(node){
      console.log('after ' + node.target.id);
    },

    onDel(node) {
     console.log(node)
     node.remove()
    },

   onChangeName(params) {
     console.log(params)
   },

   onAddNode(params) {
     console.log(params)
   },

   onClick(params) {
     console.log(params)
   },

   addNode() {
     var node = new TreeNode({ name: 'new node', isLeaf: false })
     if (!this.data.children) this.data.children = []
     this.data.addChildren(node)
   },

   getNewTree() {
     var vm = this
     function _dfs(oldNode) {
       var newNode = {}

       for (var k in oldNode) {
         if (k !== 'children' && k !== 'parent') {
           newNode[k] = oldNode[k]
         }
       }

       if (oldNode.children && oldNode.children.length > 0) {
         newNode.children = []
         for (var i = 0, len = oldNode.children.length; i < len; i++) {
           newNode.children.push(_dfs(oldNode.children[i]))
         }
       }
       return newNode
     }

     vm.newTree = _dfs(vm.data)
   }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>

<style lang="scss" rel="stylesheet/sass">
  .vtl {
    .vtl-drag-disabled {
      background-color: #d0cfcf;
      &:hover {
        background-color: #d0cfcf;
      }
    }
    .vtl-disabled {
      background-color: #d0cfcf;
    }
  }
</style>

<style lang="scss" rel="stylesheet/sass" scoped>
  .icon {
    &:hover {
      cursor: pointer;
    }
  }

  .muted {
    color: gray;
    font-size: 80%;
  }
</style>
